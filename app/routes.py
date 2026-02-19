from flask import Blueprint, abort, jsonify, request, render_template
from app import db
from app.models import TechnicalDebt

# Create a blueprint or use current_app for route definitions
api=Blueprint('api', __name__)
