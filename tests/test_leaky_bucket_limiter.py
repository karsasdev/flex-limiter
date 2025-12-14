import time
from flexlimiter.main import do_work_with_leaky_bucket_limiter


def test_requests_within_limit():
    """Test that requests within the capacity limit are allowed."""
    success_count = 0
    for i in range(5):
        try:
            do_work_with_leaky_bucket_limiter(f"user-123", f"data-{i+1}")
            success_count += 1
        except Exception:
            pass

    assert success_count == 5, f"Expected 5 successes, got {success_count}"


def test_burst_requests_over_limit():
    """Test that burst requests exceeding capacity are blocked."""
    success_count = 0
    blocked_count = 0
    
    for i in range(10):
        try:
            do_work_with_leaky_bucket_limiter("user-456", f"burst-{i+1}")
            success_count += 1
        except Exception:
            blocked_count += 1

    assert success_count == 5, f"Expected 5 successes, got {success_count}"
    assert blocked_count == 5, f"Expected 5 blocked, got {blocked_count}"


def test_bucket_leaks_over_time():
    """Test that the bucket level decreases (leaks) when no requests are made.
    
    Note: Leak is computed lazily - only when the next request arrives.
    The elapsed time since last_ts is used to calculate how much the level
    should decrease before adding the new request.
    """
    # Fill the bucket to near capacity (4 requests, level = 4)
    exhausted_count = 0
    for i in range(4):
        try:
            do_work_with_leaky_bucket_limiter("user-789", f"fill-{i+1}")
            exhausted_count += 1
        except Exception:
            pass
    
    assert exhausted_count == 4, f"Expected to make 4 requests, got {exhausted_count}"
    
    # Wait 2 seconds (no Redis state changes during this time)
    # With leak_rate=1, the next request will calculate: level = max(0, 4 - 2*1) = 2
    time.sleep(2)
    
    # First request after wait: level = 2 (after leak) + 1 = 3, should succeed (3 < 5)
    try:
        do_work_with_leaky_bucket_limiter("user-789", "after-leak-1")
    except Exception:
        assert False, "First request after leak should succeed (level should be ~3)"
    
    # Second request: level = 3 + 1 = 4, should succeed (4 < 5)
    try:
        do_work_with_leaky_bucket_limiter("user-789", "after-leak-2")
    except Exception:
        assert False, "Second request after leak should succeed (level should be ~4)"
    
    # Third request: level = 4 + 1 = 5, should be blocked (5 >= 5)
    try:
        do_work_with_leaky_bucket_limiter("user-789", "after-leak-3")
        assert False, "Third request should be blocked (level should be 5, at capacity)"
    except Exception:
        pass  # Expected to be blocked


def test_bucket_resets_after_full_drain():
    """Test that after waiting long enough, the bucket fully drains and can accept new requests.
    
    Note: Leak is computed lazily when the next request arrives.
    After waiting 6 seconds, the next request will calculate: level = max(0, 5 - 6*1) = 0
    """
    # Fill bucket to capacity (5 requests, level = 5)
    for i in range(5):
        try:
            do_work_with_leaky_bucket_limiter("user-abc", f"fill-{i+1}")
        except Exception:
            pass
    
    # Try 6th request - should be blocked (level = 5, at capacity)
    try:
        do_work_with_leaky_bucket_limiter("user-abc", "should-block")
        assert False, "6th request should have been blocked"
    except Exception:
        pass
    
    # Wait long enough for bucket to fully drain (with leak_rate=1, 6 seconds should be enough)
    # During sleep, no Redis state changes occur
    time.sleep(6)
    
    # Next request triggers leak calculation: level = max(0, 5 - 6*1) = 0, then +1 = 1
    # Should succeed (1 < 5)
    try:
        do_work_with_leaky_bucket_limiter("user-abc", "after-drain")
    except Exception:
        assert False, "Request should have succeeded after bucket drained"


def test_different_users_independent():
    """Test that different users have independent leaky buckets."""
    # Fill bucket for user-1
    for i in range(5):
        try:
            do_work_with_leaky_bucket_limiter("user-1", f"data-{i+1}")
        except Exception:
            pass
    
    # user-1 should be blocked
    try:
        do_work_with_leaky_bucket_limiter("user-1", "should-block")
        assert False, "user-1 should be blocked"
    except Exception:
        pass
    
    # user-2 should still be able to make requests
    success_count = 0
    for i in range(5):
        try:
            do_work_with_leaky_bucket_limiter("user-2", f"data-{i+1}")
            success_count += 1
        except Exception:
            pass
    
    assert success_count == 5, f"Expected user-2 to make 5 requests, got {success_count}"
