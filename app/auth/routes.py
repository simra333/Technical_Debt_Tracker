from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from app.models import User
from app import db
from app.auth.services import hash_password, verify_password

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()

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

    user = User.query.filter_by(username=data['username']).first()

    if user and verify_password(data['password'], user.password_hash):
        session['user_id'] = user.id
        return jsonify({'message': 'Login successful'})
    
    return jsonify({'message': 'Invalid username or password'}), 401

@auth.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@auth.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login_page'))