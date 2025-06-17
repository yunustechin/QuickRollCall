from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    BASE_URL: str = "http://127.0.0.1:5000"


class RateLimitConfig(BaseSettings):
    REQUESTS_LIMIT: int = 2
    TIME_WINDOW: int = 60  # seconds

app_settings = AppConfig()
rate_limit_settings = RateLimitConfig()