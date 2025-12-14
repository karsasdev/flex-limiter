import pytest
from flexlimiter.init import load_redis


@pytest.fixture(scope="function", autouse=True)
def clear_redis_before_test():
    r = load_redis()
    pipe = r.pipeline()
    for pattern in (
        "token_bucket_rate_limit:*",
        "leaky_bucket_rate_limit:*",
        "sliding_window_counter_rate_limit:*"
    ):
        for key in r.scan_iter(match=pattern):
            pipe.delete(key)
    pipe.execute()


@pytest.fixture(scope="session", autouse=True)
def clear_redis_after_session():
    yield
    r = load_redis()
    pipe = r.pipeline()
    for pattern in (
        "token_bucket_rate_limit:*",
        "leaky_bucket_rate_limit:*",
        "sliding_window_counter_rate_limit:*"
    ):
        for key in r.scan_iter(match=pattern):
            pipe.delete(key)
    pipe.execute()

