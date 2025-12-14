from flexlimiter.config import settings
from flexlimiter.init import load_lua_script, LUA_SCRIPTS, ALGO_ARG_MAP, load_redis

from functools import wraps

def rate_limiter(algo: str):
    if algo not in LUA_SCRIPTS:
        raise ValueError(f"Unknown limiter algorithm: {algo}")
    lua_script = load_lua_script(LUA_SCRIPTS[algo])

    def decorator(func):
        @wraps(func)
        def wrapper(key, *args, **kwargs):

            argv = ALGO_ARG_MAP[algo](settings)
            
            allowed = redis_client.eval(
                lua_script,
                1,
                key,
                *argv
            )

            if allowed != 1:
                raise Exception("429 Too Many Requests")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def do_work(data):
    return f"processed: {data}"
    
redis_client = load_redis()
do_work_with_token_bucket_limiter = rate_limiter("token_bucket")(do_work)
do_work_with_leaky_bucket_limiter = rate_limiter("leaky_bucket")(do_work)
do_work_with_sliding_window_counter_limiter = rate_limiter("sliding_window_counter")(do_work)

if __name__ == '__main__':
    do_work_with_token_bucket_limiter("user-1234", "test")
    do_work_with_leaky_bucket_limiter("user-2343", "test")
    do_work_with_sliding_window_counter_limiter("user-3453", "test")