from flask import Blueprint, abort, jsonify, request, render_template
from app import db
from app.models import TechnicalDebt

# Create a blueprint or use current_app for route definitions
api=Blueprint('api', __name__)

# API Routes (return JSON data)
@api.route('/api/debts', methods=['GET']) # Get all technical debt items
def get_debts():
    debts = TechnicalDebt.query.all()
    return jsonify([debt.to_dict() for debt in debts])

@api.route('api/debts/<int:debt_id>', methods=['GET']) # Get a specific technical debt item by ID
def get_debt(debt_id):
    debt = TechnicalDebt.query.get(debt_id)
    if debt is None:
        abort(404, description="Technical debt item not found")
    return jsonify({
        'id': debt.id,
        'title': debt.title,
        'description': debt.description,
        'risk': debt.risk,
        'effort_estimate': debt.effort_estimate,
        'status': debt.status,
        'assigned_to': debt.assigned_to,
        'created_at': debt.created_at.isoformat()
    })