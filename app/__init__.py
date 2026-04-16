from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from azure.monitor.opentelemetry import configure_azure_monitor
import logging
import os

db = SQLAlchemy()                           # Create the database object

# Logging setup
logger = logging.getLogger(__name__)

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    )

def setup_monitoring():
    connection_string = os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING')

    if not connection_string:
        logger.warning("Azure Monitor NOT configured (missing connection string)")
        return

    configure_azure_monitor(
        connection_string=connection_string,
    )

    logging.getLogger().setLevel(logging.INFO)
    
    logger.info("Azure Monitor configured successfully")


def create_app(config_class=Config):
    setup_logging()                        
    setup_monitoring()                      

    app=Flask(__name__)
    app.config.from_object(config_class)          # Load configuration

    app.secret_key = os.environ.get("SECRET_KEY", "dev-only-fallback")  # Set secret key for session management

    db.init_app(app)                        # Initialise the database with this app
        
    from app.routes import api              
    app.register_blueprint(api)

    from app.auth.routes import auth
    app.register_blueprint(auth)
 
    with app.app_context():                  # Create database tables
        db.create_all()

    return app