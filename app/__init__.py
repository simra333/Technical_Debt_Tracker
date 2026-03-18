from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
import logging
import os

db = SQLAlchemy()                           # Create the database object

# Logging setup
logger = logging.getLogger(__name__)
logger.addHandler(
    AzureLogHandler(
        connection_string=os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING']
    )
)

logger.warning("Application Insights is working!")

def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)          # Load configuration

    db.init_app(app)                        # Initialise the database with this app

    # Request Tracking setup
    middleware = FlaskMiddleware(
        app,
        exporter_options={
            'connection_string': os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING']
        }
    )

    from app.routes import api              
    app.register_blueprint(api)
 
    with app.app_context():                  # Create database tables
        db.create_all()

    return app