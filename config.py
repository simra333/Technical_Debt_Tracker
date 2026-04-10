import os

class Config:

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///technical_debt.db')

    # Other configurations settings
    DEBBUG = True

    FEATURE_FLAGS = {
        "CATEGORY_DROPDOWN": os.getenv("FF_CATEGORY_DROPDOWN", "false").lower() == "true"
    }