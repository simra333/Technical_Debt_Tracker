from flask import Blueprint, abort, jsonify, request, render_template, current_app
from sqlalchemy import text
from app import db, logger
from app.models import TechnicalDebt
from app.auth.decorators import api_login_required, ui_login_required

# Create a blueprint or use current_app for route definitions
api=Blueprint('api', __name__)

@api.route('/health', methods=['GET'])
def health():
    try: 
        # Check database connectivity by executing a simple query
        db.session.execute(text('SELECT 1'))  
        return {
            "status": "healthy",
            "database": "connected"
        }, 200
    except Exception as e:
        logger.exception("Health check failed")
        return {"status": "unhealthy", "error": str(e)}, 500
    

# API Routes (return JSON data)
@api.route('/api/debts', methods=['GET']) 
@api_login_required
def get_debts():
    """Get all technical debt items"""
    debts = TechnicalDebt.query.all()
    return jsonify([debt.to_dict() for debt in debts])

@api.route('/api/debts/<int:debt_id>', methods=['GET']) 
@api_login_required
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
@api_login_required
def create_debt():
    """ Create a new techical debt item"""
    data = request.get_json()

    logger.info("POST /api/debts called")
    logger.info(f"incoming data: {data}")

    if not data.get('title'):
        logger.warning(f"Validation error: Missing title. Payload: {data}")
        return jsonify({"error": "Title is required"}), 400

    try:
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

        logger.info(f"Technical debt item created successfully with ID: {new_debt.id}")
        logger.info(f"metric=debt_created risk={new_debt.risk}")
        
        logger.warning("metric=debt_creation_failed count=1 reason=validation_error")

        return jsonify(new_debt.to_dict()), 201
    
    except Exception as e:
        logger.exception("Error creating technical debt item")
        return jsonify({"error": "Internal Server Error"}), 500

@api.route('/api/debts/<int:debt_id>', methods=['PUT']) 
@api_login_required
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
@api_login_required
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
@ui_login_required
def index():
    """Render the main page"""
    return render_template('index.html')

@api.route('/add')
@ui_login_required
def add_debt_ui():
    use_category_dropdown = current_app.config['FEATURE_FLAGS'].get('CATEGORY_DROPDOWN', False)
    """Render the page to add a new technical debt item"""
    return render_template('add.html', use_category_dropdown=use_category_dropdown)

@api.route('/edit/<int:debt_id>')
@ui_login_required
def edit_ui(debt_id):
    """Render the page to edit an existing technical debt item"""
    # fetch the debt item from the database to pre-populate the form 
    debt_item = db.session.get(TechnicalDebt, debt_id)
    if not debt_item:
        return "Debt item not found", 404
    use_category_dropdown = current_app.config['FEATURE_FLAGS'].get('CATEGORY_DROPDOWN', False)
    return render_template('edit.html', debt_id=debt_id, debt_item=debt_item, use_category_dropdown=use_category_dropdown)
    