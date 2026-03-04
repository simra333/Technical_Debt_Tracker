from flask import Blueprint, abort, jsonify, request, render_template
from app import db
from app.models import TechnicalDebt

# Create a blueprint or use current_app for route definitions
api=Blueprint('api', __name__)

# API Routes (return JSON data)
@api.route('/api/debts', methods=['GET']) 
def get_debts():
    """Get all technical debt items"""
    debts = TechnicalDebt.query.all()
    return jsonify([debt.to_dict() for debt in debts])

@api.route('/api/debts/<int:debt_id>', methods=['GET']) 
def get_debt(debt_id):
    """Get a specific technical debt item by ID"""
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

@api.route('/api/debts', methods=['POST']) 
def create_debt():
    """ Create a new techical debt item"""
    data = request.get_json()

    new_debt = TechnicalDebt(
        title=data['title'],
        description=data['description'],
        risk=data['risk'],
        effort_estimate=data['effort_estimate'],
        status=data.get('status', 'Open'),
        assigned_to=data.get('assigned_to')
    )

    db.session.add(new_debt)
    db.session.commit()
    return jsonify(new_debt.to_dict()), 201

@api.route('/api/debts/<int:debt_id>', methods=['PUT']) 
def update_debt(debt_id):
    """Update an existing technical debt item"""
    debt = db.session.get(TechnicalDebt,debt_id)
    if debt is None:
        abort(404, description="Technical debt item not found")

    data = request.get_json()
    if 'title' in data:
        debt.title = data['title']
    if 'description' in data:
        debt.description = data['description']
    if 'risk' in data:
        debt.risk = data['risk']
    if 'effort_estimate' in data:
        debt.effort_estimate = data['effort_estimate']
    if 'status' in data:
        debt.status = data['status']
    if 'assigned_to' in data:
        debt.assigned_to = data['assigned_to']

    db.session.commit()
    return jsonify({
        'id': debt.id,
        'title': debt.title,
        'description': debt.description,
        'risk': debt.risk,
        'effort_estimate': debt.effort_estimate,
        'status': debt.status,
        'assigned_to': debt.assigned_to,
        'created_at': debt.created_at.isoformat()
    }), 200

@api.route('/api/debts/<int:debt_id>', methods=['DELETE'])
def delete_debt(debt_id):
    """Delete a technical debt item"""
    debt = db.session.get(TechnicalDebt, debt_id)
    if debt is None:
        abort(404, description="Technical debt item not found")

    db.session.delete(debt)
    db.session.commit()
    return jsonify({'message': 'Technical debt item deleted successfully'}), 204

# UI Routes (render HTML templates)
@api.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@api.route('/add')
def add_debt_ui():
    """Render the page to add a new technical debt item"""
    return render_template('add.html')

@api.route('/edit/<int:debt_id>')
def edit_ui(debt_id):
    """Render the page to edit an existing technical debt item"""
    return render_template('edit.html', debt_id=debt_id)
    