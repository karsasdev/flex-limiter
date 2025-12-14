import time
from flexlimiter.main import do_work_with_token_bucket_limiter


def test_requests_within_limit():
    success_count = 0
    for i in range(5):
        try:
            do_work_with_token_bucket_limiter(f"user-123", f"data-{i+1}")
            success_count += 1
        except Exception:
            pass

    assert success_count == 5, f"Expected 5 successes, got {success_count}"


def test_burst_requests_over_limit():
    success_count = 0
    blocked_count = 0
    
    for i in range(10):
        try:
            do_work_with_token_bucket_limiter("user-456", f"burst-{i+1}")
            success_count += 1
        except Exception:
            blocked_count += 1

    assert success_count == 5, f"Expected 5 successes, got {success_count}"
    assert blocked_count == 5, f"Expected 5 blocked, got {blocked_count}"


def test_token_refill_after_wait():
    exhausted_count = 0
    for i in range(5):
        try:
            do_work_with_token_bucket_limiter("user-789", f"exhaust-{i+1}")
            exhausted_count += 1
        except Exception:
            pass
    
    assert exhausted_count == 5, f"Expected to exhaust all 5 tokens, got {exhausted_count}"
    
    try:
        do_work_with_token_bucket_limiter("user-789", "should-block")
        assert False, "6th request should have been blocked"
    except Exception:
        pass
    
    time.sleep(2)
    
    try:
        do_work_with_token_bucket_limiter("user-789", "after-refill")
    except Exception:
        assert False, "Request should have succeeded after refill"

