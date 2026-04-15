import os

class Config:

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:////app/instance/technical_debt.db')

    # Other configurations settings
    DEBUG = True

    FEATURE_FLAGS = {
        "CATEGORY_DROPDOWN": os.getenv("FF_CATEGORY_DROPDOWN", "false").lower() == "true"
    }