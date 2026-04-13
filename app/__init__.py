from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from azure.monitor.opentelemetry import configure_azure_monitor
import logging
import os

db = SQLAlchemy()                           # Create the database object

def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)          # Load configuration

    app.secret_key = os.environ.get("SECRET_KEY", "dev-only-fallback")  # Set secret key for session management

    db.init_app(app)                        # Initialise the database with this app

    # Logging setup
    connection_string = os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING')
    if connection_string:
        configure_azure_monitor(connection_string=connection_string)
        logging.info("Azure Monitor configured successfully.")
        
    from app.routes import api              
    app.register_blueprint(api)

    from app.auth.routes import auth
    app.register_blueprint(auth)
 
    with app.app_context():                  # Create database tables
        db.create_all()

    return app