from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
import logging
import os

db = SQLAlchemy()                           # Create the database object

def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)          # Load configuration

    db.init_app(app)                        # Initialise the database with this app

    # Logging setup
    connection_string = os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING')
    if connection_string:
        logger = logging.getLogger('app')

        if not logger.hasHandlers():  # Avoid adding multiple handlers in development
            logger.addHandler(
                AzureLogHandler(connection_string=connection_string)
            )
        # Request Tracking setup
        FlaskMiddleware(
            app,
            exporter=AzureExporter(
                connection_string=connection_string
            ),
            sampler=ProbabilitySampler(rate=1.0)
        )
        logger.warning("Application Insights is working!")

    from app.routes import api              
    app.register_blueprint(api)
 
    with app.app_context():                  # Create database tables
        db.create_all()

    return app