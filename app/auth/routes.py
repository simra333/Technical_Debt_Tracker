from flask import request, jsonify, session, render_template, redirect, url_for
from app.models import User
from app import db
from app.auth.services import hash_password, verify_password
from app.auth import auth

# UI routes for browser-based access

@auth.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@auth.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login_page'))

# API routes for testing purposes (postman)

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Invalid input'}), 400

    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        password_hash=hash_password(data['password'])
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Invalid input'}), 400
    user = User.query.filter_by(username=data['username']).first()

    # verify username and password
    if user and verify_password(data['password'], user.password_hash):
        session['user_id'] = user.id
        return jsonify({'message': 'Login successful'}), 200
    
    return jsonify({'message': 'Invalid username or password'}), 401

@auth.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200

