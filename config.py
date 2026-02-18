import os

class Config:

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///technical_debt.db')

    # Other configurations settings
    Debug = True