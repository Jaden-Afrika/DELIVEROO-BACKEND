import os
from datetime import timedelta


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 86400))
    )
    FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")
    API_PREFIX = os.environ.get("API_PREFIX", "")
    GEOCODING_PROVIDER = os.environ.get("GEOCODING_PROVIDER", "stub")
    ROUTING_PROVIDER = os.environ.get("ROUTING_PROVIDER", "stub")
    PAYMENT_PROVIDER = os.environ.get("PAYMENT_PROVIDER", "stub")
    STORAGE_PROVIDER = os.environ.get("STORAGE_PROVIDER", "local")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", "sqlite:///:memory:"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=60)
