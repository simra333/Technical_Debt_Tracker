import os

class Config:

    SECRET_KEY = os.getenv("SECRET_KEY")

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:////app/instance/technical_debt.db')

    # Other configurations settings
    DEBUG = True

    FEATURE_FLAGS = {
        "CATEGORY_DROPDOWN": os.getenv("FF_CATEGORY_DROPDOWN", "false").lower() == "true"
    }

class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'