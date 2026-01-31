"""Configuration Management - 配置管理模块"""
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    username: str = "postgres"
    password: str = "postgres"
    name: str = "cv_algorithm_hub"
    pool_size: int = 10
    max_overflow: int = 20

    @property
    def url(self) -> str:
        # Use psycopg2 for sync connections
        return f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisConfig(BaseModel):
    """Redis configuration"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None


class RabbitMQConfig(BaseModel):
    """RabbitMQ configuration"""
    host: str = "localhost"
    port: int = 5672
    username: str = "guest"
    password: str = "guest"
    virtual_host: str = "/"


class GPUSettings(BaseModel):
    """GPU configuration"""
    enabled: bool = True
    device_id: int = 0
    memory_limit: int = 0  # 0 means no limit
    cuda_version: str = "11.8"


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None


class SecurityConfig(BaseModel):
    """Security configuration"""
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours


class Settings(BaseSettings):
    """Application settings"""
    # Metadata
    app_name: str = "CV Algorithm Hub"
    app_version: str = "1.0.0"
    environment: str = "development"

    # Database - use individual fields for env var support
    database_host: str = "localhost"
    database_port: int = 5432
    database_username: str = "postgres"
    database_password: str = "postgres"
    database_name: str = "cv_algorithm_hub"

    # Redis
    redis: RedisConfig = Field(default_factory=RedisConfig)

    # RabbitMQ
    rabbitmq: RabbitMQConfig = Field(default_factory=RabbitMQConfig)

    # GPU
    gpu: GPUSettings = Field(default_factory=GPUSettings)

    # Logging
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    # Security - direct attributes for convenience
    secret_key: str = "change-me-in-production-min-32-chars-long"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # CORS - store as comma-separated string in env, parse to list
    cors_origins_str: str = "http://localhost:3000,http://localhost:5173"

    # Paths
    data_dir: Path = Path("./data")
    models_dir: Path = Path("./models")
    temp_dir: Path = Path("./temp")

    @property
    def database(self) -> DatabaseConfig:
        """Get database config from individual fields"""
        return DatabaseConfig(
            host=self.database_host,
            port=self.database_port,
            username=self.database_username,
            password=self.database_password,
            name=self.database_name
        )

    @property
    def cors_origins(self) -> List[str]:
        """Parse cors_origins_str to list"""
        return [origin.strip() for origin in self.cors_origins_str.split(",")]

    model_config = SettingsConfigDict(
        env_prefix="CVHUB_",
        case_sensitive=False,
        env_ignore_missing=True
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Create a global settings instance for easy import
settings = get_settings()
