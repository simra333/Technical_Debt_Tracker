from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()                           # Create the database object

def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)          # Load configuration

    db.init_app(app)                        # Initialise the database with this app

    from app.routes import api              
    app.register_blueprint(api)
 
    with app.app_context():                  # Create database tables
        db.create_all()

    return app