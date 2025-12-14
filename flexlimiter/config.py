from pydantic import computed_field
from pydantic_settings import BaseSettings


class FlexLimiterConfig(BaseSettings):
    REDIS_LIMITER_STORE_HOST: str = "localhost"
    REDIS_LIMITER_STORE_PORT: str = "6379"
    REDIS_LIMITER_STORE_PASSWORD: str = "mypass"
    REDIS_LIMITER_STORE_DB_INDEX: str = "1"

    TOKEN_BUCKET_CAPACITY: int = 5
    TOKEN_BUCKET_REFILL_RATE: int = 1

    LEAKY_BUCKET_CAPACITY: int = 5
    LEAKY_BUCKET_LEAK_RATE: int = 1

    SLIDING_WINDOW_COUNTER_WINDOW_SIZE: int = 60
    SLIDING_WINDOW_COUNTER_BUCKET_SIZE: int = 60
    SLIDING_WINDOW_COUNTER_REQUESTS_PER_WINDOW: int = 60

    @computed_field
    @property
    def REDIS_LIMITER_STORE_URI(self) -> str:
        return (
            f"redis://:{self.REDIS_LIMITER_STORE_PASSWORD}@{self.REDIS_LIMITER_STORE_HOST}"
            f":{self.REDIS_LIMITER_STORE_PORT}/{self.REDIS_LIMITER_STORE_DB_INDEX}"
        )

settings = FlexLimiterConfig()