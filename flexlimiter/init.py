import redis
from pathlib import Path

from flexlimiter.config import settings


LUA_SCRIPTS = {
    "token_bucket": "token_bucket.lua",
    "leaky_bucket": "leaky_bucket.lua",
    "sliding_window_counter": "sliding_window_counter.lua",
}
ALGO_ARG_MAP = {
    "token_bucket": lambda s: [
        s.TOKEN_BUCKET_CAPACITY,
        s.TOKEN_BUCKET_REFILL_RATE,
    ],
    "leaky_bucket": lambda s: [
        s.LEAKY_BUCKET_CAPACITY,
        s.LEAKY_BUCKET_LEAK_RATE,
    ],
    "sliding_window_counter": lambda s: [
        s.SLIDING_WINDOW_COUNTER_WINDOW_SIZE,
        s.SLIDING_WINDOW_COUNTER_BUCKET_SIZE,
        s.SLIDING_WINDOW_COUNTER_REQUESTS_PER_WINDOW,
    ],
}

def load_redis():
    r = redis.Redis(
        host=settings.REDIS_LIMITER_STORE_HOST,
        port=int(settings.REDIS_LIMITER_STORE_PORT),
        password=settings.REDIS_LIMITER_STORE_PASSWORD,
        db=int(settings.REDIS_LIMITER_STORE_DB_INDEX),
        decode_responses=True,
    )
    return r

def load_lua_script(path: str) -> str:
    # Resolve path relative to the lua directory
    lua_dir = Path(__file__).parent / "lua"
    script_path = lua_dir / path
    with open(script_path, "r") as f:
        return f.read()
