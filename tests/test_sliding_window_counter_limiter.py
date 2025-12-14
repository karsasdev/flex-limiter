import time
import pytest
from flexlimiter.main import do_work_with_sliding_window_counter_limiter
from flexlimiter.config import settings


def test_requests_within_window_allowed():
    """Requests within the sliding window limit should be allowed."""
    success = 0
    for i in range(settings.SLIDING_WINDOW_COUNTER_REQUESTS_PER_WINDOW):
        try:
            do_work_with_sliding_window_counter_limiter(
                "user-1", f"data-{i}"
            )
            success += 1
        except Exception:
            pass

    assert success == settings.SLIDING_WINDOW_COUNTER_REQUESTS_PER_WINDOW


def test_requests_exceeding_window_blocked():
    """Requests exceeding the window limit should be blocked."""
    success = 0
    blocked = 0

    for i in range(settings.SLIDING_WINDOW_COUNTER_REQUESTS_PER_WINDOW + 10):
        try:
            do_work_with_sliding_window_counter_limiter(
                "user-2", f"burst-{i}"
            )
            success += 1
        except Exception:
            blocked += 1

    assert success == settings.SLIDING_WINDOW_COUNTER_REQUESTS_PER_WINDOW
    assert blocked == 10


def test_sliding_window_weighted_previous_bucket():
    """
    Validate weighted contribution of previous bucket.
    """
    # Fill part of previous bucket
    for i in range(30):
        do_work_with_sliding_window_counter_limiter(
            "user-3", f"prev-{i}"
        )

    # Move halfway into the next window
    time.sleep(settings.SLIDING_WINDOW_COUNTER_WINDOW_SIZE // 2)

    success = 0
    blocked = 0

    for i in range(50):
        try:
            do_work_with_sliding_window_counter_limiter(
                "user-3", f"curr-{i}"
            )
            success += 1
        except Exception:
            blocked += 1

    # prev contribution ≈ 30 * 0.5 = 15
    # allowed curr ≈ REQUESTS_PER_WINDOW - 15
    assert success <= (
        settings.SLIDING_WINDOW_COUNTER_REQUESTS_PER_WINDOW - 15
    )
    assert blocked >= 5


def test_window_resets_after_full_window_passes():
    """
    For Sliding Window Counter, the state fully clears only after
    both current and previous buckets expire.
    """
    # Fill up to the limit
    for i in range(settings.SLIDING_WINDOW_COUNTER_REQUESTS_PER_WINDOW):
        do_work_with_sliding_window_counter_limiter(
            "user-4", f"fill-{i}"
        )

    # Should be blocked immediately
    with pytest.raises(Exception):
        do_work_with_sliding_window_counter_limiter(
            "user-4", "should-block"
        )

    # Wait long enough for both buckets to expire
    time.sleep(settings.SLIDING_WINDOW_COUNTER_WINDOW_SIZE * 2 + 1)

    success = 0
    for i in range(settings.SLIDING_WINDOW_COUNTER_REQUESTS_PER_WINDOW):
        try:
            do_work_with_sliding_window_counter_limiter(
                "user-4", f"after-reset-{i}"
            )
            success += 1
        except Exception:
            pass

    assert success == settings.SLIDING_WINDOW_COUNTER_REQUESTS_PER_WINDOW


def test_different_users_independent_windows():
    """Each user should have an independent sliding window."""
    for i in range(settings.SLIDING_WINDOW_COUNTER_REQUESTS_PER_WINDOW):
        do_work_with_sliding_window_counter_limiter(
            "user-a", f"a-{i}"
        )

    with pytest.raises(Exception):
        do_work_with_sliding_window_counter_limiter(
            "user-a", "blocked"
        )

    success = 0
    for i in range(settings.SLIDING_WINDOW_COUNTER_REQUESTS_PER_WINDOW):
        try:
            do_work_with_sliding_window_counter_limiter(
                "user-b", f"b-{i}"
            )
            success += 1
        except Exception:
            pass

    assert success == settings.SLIDING_WINDOW_COUNTER_REQUESTS_PER_WINDOW
