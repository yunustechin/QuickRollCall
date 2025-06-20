from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    """
    Defines general configuration for the application's runtime environment.
    
    These settings control the server's network interface and may include
    IP addresses for special clients (e.g., for testing or development).
    """
    CLIENT_IP: str = "0.0.0.0"
    PORT: int = 5000

class RateLimitConfig(BaseSettings):
    """
    Configures the settings for the API rate limiter.

    This determines how many requests a single client can make within a given
    period, preventing abuse and ensuring service stability.
    """
    REQUESTS_LIMIT: int = 2
    TIME_WINDOW: int = 60 

class AccessTokenConfig(BaseSettings):
    """
    Manages the lifecycle and validity of one-time access tokens.
    
    These tokens are typically used for securing single-use actions, such as
    accessing a form after scanning a QR code.
    """
    EXPIRE_SECONDS: int = 60

app_settings = AppConfig()
rate_limit_settings = RateLimitConfig()
access_token_settings = AccessTokenConfig()