from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user
from models import db
from models.user import User

auth = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth.post('/register')
def register():
    data = request.get_json() or {}
    required = ['full_name', 'email', 'password', 'contact_number']
    errors = [f'{field} is required.' for field in required if not data.get(field)]
    if data.get('role') and data.get('role') != 'user':
        errors.append('Role spoofing is not allowed.')
    if User.query.filter_by(email=data.get('email')).first():
        errors.append('Email already exists.')
    if errors:
        return jsonify({'errors': errors}), 400
    user = User(full_name=data['full_name'], email=data['email'], contact_number=data['contact_number'], role='user', status='active')
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Registration successful.'}), 201

@auth.post('/login')
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get('email')).first()
    if not user or not user.check_password(data.get('password', '')):
        return jsonify({'error': 'Invalid credentials.'}), 401
    if user.status != 'active':
        return jsonify({'error': 'Account is inactive.'}), 403
    login_user(user)
    return jsonify({'message': 'Login successful.', 'user': {'id': user.id, 'full_name': user.full_name, 'role': user.role}})

@auth.post('/logout')
def logout():
    logout_user()
    return jsonify({'message': 'Logged out.'})

@auth.get('/me')
def me():
    if not current_user.is_authenticated:
        return jsonify({'authenticated': False}), 401
    return jsonify({'authenticated': True, 'user': {'id': current_user.id, 'full_name': current_user.full_name, 'email': current_user.email, 'role': current_user.role}})
