from urllib.parse import quote_plus

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "ITIP Backend"
    API_V1_STR: str = "/v1"
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Database
    POSTGRES_USER: str = Field(min_length=1)
    POSTGRES_PASSWORD: str = Field(min_length=16)
    POSTGRES_HOST: str = Field(min_length=1)
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = Field(min_length=1)

    # Observability
    OTEL_SERVICE_NAME: str = "itip-backend"
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = None
    OTEL_CONSOLE_EXPORTER: bool = False

    @property
    def sqlalchemy_database_uri(self) -> str:
        user = quote_plus(self.POSTGRES_USER)
        raw_password = (
            self.POSTGRES_PASSWORD.get_secret_value()
            if isinstance(self.POSTGRES_PASSWORD, SecretStr)
            else self.POSTGRES_PASSWORD
        )
        password = quote_plus(raw_password)
        database = quote_plus(self.POSTGRES_DB)
        return f"postgresql://{user}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{database}"

    @model_validator(mode="after")
    def reject_insecure_values(self) -> "Settings":
        if self.SECRET_KEY.lower() in {"default_insecure_secret_key", "changeme", "secret"}:
            raise ValueError("SECRET_KEY must be a unique, high-entropy secret")
        raw_password = (
            self.POSTGRES_PASSWORD.get_secret_value()
            if isinstance(self.POSTGRES_PASSWORD, SecretStr)
            else self.POSTGRES_PASSWORD
        )
        if raw_password.lower() in {"itip_secret", "password", "changeme"}:
            raise ValueError("POSTGRES_PASSWORD must not use a default password")
        return self
    
    # APIs
    FIRMS_API_KEY: SecretStr | None = None
    MAP_API_KEY: SecretStr | None = None
    WEATHER_API_KEY: SecretStr | None = None
    TARGET_REGION_BBOX: str = "-124.4,32.5,-114.1,42.0"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
