from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from models import db
from models.user import User
from models.trek import Trek
from models.booking import Booking
from services.report_service import build_monthly_html
from utils.auth import role_required
from utils.validators import validate_trek_payload, ALLOWED_USER_STATUS
from extensions import cache

admin = Blueprint('admin', __name__, url_prefix='/api/admin')

def clear_trek_cache():
    try:
        cache.clear()
    except Exception:
        pass

@admin.get('/dashboard')
@role_required('admin')
def dashboard():
    stats = {
        'treks': Trek.query.count(),
        'users': User.query.filter_by(role='user').count(),
        'staff': User.query.filter_by(role='staff').count(),
        'bookings': Booking.query.count()
    }
    recent = Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()
    trek_counts = {}
    for b in Booking.query.all():
        if b.trek:
            trek_counts[b.trek.trek_name] = trek_counts.get(b.trek.trek_name, 0) + 1
    return jsonify({
        'stats': stats,
        'recent_bookings': [{'id': b.id, 'user_name': b.user.full_name, 'trek_name': b.trek.trek_name, 'status': b.status, 'payment_status': b.payment_status} for b in recent],
        'popular_treks': trek_counts
    })

@admin.get('/treks')
@role_required('admin')
def get_treks():
    items = Trek.query.order_by(Trek.id.desc()).all()
    return jsonify({'items': [serialize_trek(t) for t in items]})

@admin.post('/treks')
@role_required('admin')
def create_trek():
    data = request.get_json() or {}
    errors = validate_trek_payload(data)
    if data.get('assigned_staff_id'):
        staff = db.session.get(User, int(data['assigned_staff_id']))
        if not staff or staff.role != 'staff' or staff.status != 'active':
            errors.append('Assigned staff must be an active staff member.')
    if errors:
        return jsonify({'errors': errors}), 400
    trek = Trek(**normalize_trek_data(data))
    db.session.add(trek)
    db.session.commit()
    clear_trek_cache()
    return jsonify({'message': 'Trek created.', 'item': serialize_trek(trek)}), 201

@admin.put('/treks/<int:trek_id>')
@role_required('admin')
def update_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found.'}), 404
    data = request.get_json() or {}
    errors = validate_trek_payload(data)
    if data.get('assigned_staff_id'):
        staff = db.session.get(User, int(data['assigned_staff_id']))
        if not staff or staff.role != 'staff' or staff.status != 'active':
            errors.append('Assigned staff must be an active staff member.')
    if errors:
        return jsonify({'errors': errors}), 400
    for key, value in normalize_trek_data(data).items():
        setattr(trek, key, value)
    db.session.commit()
    clear_trek_cache()
    return jsonify({'message': 'Trek updated.', 'item': serialize_trek(trek)})

@admin.delete('/treks/<int:trek_id>')
@role_required('admin')
def delete_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found.'}), 404
    if Booking.query.filter_by(trek_id=trek_id).count() > 0:
        return jsonify({'error': 'Cannot delete trek with historical bookings.'}), 400
    db.session.delete(trek)
    db.session.commit()
    clear_trek_cache()
    return jsonify({'message': 'Trek deleted.'})

@admin.get('/staff')
@role_required('admin')
def get_staff():
    items = User.query.filter_by(role='staff').order_by(User.id.desc()).all()
    return jsonify({'items': [serialize_user(s) for s in items]})

@admin.post('/staff')
@role_required('admin')
def create_staff():
    data = request.get_json() or {}
    required = ['full_name', 'email', 'contact_number', 'password']
    errors = [f'{f} is required.' for f in required if not data.get(f)]
    if User.query.filter_by(email=data.get('email')).first():
        errors.append('Email already exists.')
    status = data.get('status', 'active')
    if status not in ALLOWED_USER_STATUS:
        errors.append('Invalid status.')
    if errors:
        return jsonify({'errors': errors}), 400
    staff = User(full_name=data['full_name'], email=data['email'], contact_number=data['contact_number'], role='staff', status=status, experience=data.get('experience'), specialization=data.get('specialization'))
    staff.set_password(data['password'])
    db.session.add(staff)
    db.session.commit()
    return jsonify({'message': 'Staff created.'}), 201

@admin.patch('/staff/<int:user_id>/status')
@role_required('admin')
def update_staff_status(user_id):
    user = db.session.get(User, user_id)
    if not user or user.role != 'staff':
        return jsonify({'error': 'Staff not found.'}), 404
    status = (request.get_json() or {}).get('status')
    if status not in ALLOWED_USER_STATUS:
        return jsonify({'error': 'Invalid status.'}), 400
    user.status = status
    db.session.commit()
    return jsonify({'message': 'Staff status updated.'})

@admin.get('/users')
@role_required('admin')
def get_users():
    items = User.query.filter_by(role='user').order_by(User.id.desc()).all()
    return jsonify({'items': [serialize_user(u) for u in items]})

@admin.patch('/users/<int:user_id>/status')
@role_required('admin')
def update_user_status(user_id):
    user = db.session.get(User, user_id)
    if not user or user.role != 'user':
        return jsonify({'error': 'User not found.'}), 404
    status = (request.get_json() or {}).get('status')
    if status not in ALLOWED_USER_STATUS:
        return jsonify({'error': 'Invalid status.'}), 400
    user.status = status
    db.session.commit()
    return jsonify({'message': 'User status updated.'})

@admin.get('/search')
@role_required('admin')
def search_all():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'treks': [], 'users': [], 'staff': []})
    treks = Trek.query.filter(or_(Trek.trek_name.ilike(f'%{q}%'), Trek.location.ilike(f'%{q}%'), Trek.id == q if q.isdigit() else False)).all()
    users = User.query.filter(User.role == 'user').filter(or_(User.full_name.ilike(f'%{q}%'), User.email.ilike(f'%{q}%'))).all()
    staff = User.query.filter(User.role == 'staff').filter(or_(User.full_name.ilike(f'%{q}%'), User.email.ilike(f'%{q}%'))).all()
    return jsonify({'treks': [serialize_trek(t) for t in treks], 'users': [serialize_user(u) for u in users], 'staff': [serialize_user(s) for s in staff]})

@admin.get('/reports/summary')
@role_required('admin')
def report_summary():
    return jsonify({
        'treks_conducted': Trek.query.filter(Trek.status.in_(['completed', 'ongoing'])).count(),
        'participants': Booking.query.filter(Booking.status.in_(['booked', 'completed'])).count(),
        'open_treks': Trek.query.filter_by(status='open').count()
    })

@admin.get('/reports/monthly-html')
@role_required('admin')
def monthly_html():
    return build_monthly_html(), 200, {'Content-Type': 'text/html'}

def serialize_user(user):
    return {
        'id': user.id,
        'full_name': user.full_name,
        'email': user.email,
        'contact_number': user.contact_number,
        'status': user.status,
        'experience': user.experience,
        'specialization': user.specialization
    }

def serialize_trek(t):
    return {
        'id': t.id,
        'trek_name': t.trek_name,
        'location': t.location,
        'difficulty': t.difficulty,
        'duration_days': t.duration_days,
        'total_slots': t.total_slots,
        'available_slots': t.available_slots,
        'status': t.status,
        'start_date': t.start_date,
        'end_date': t.end_date,
        'altitude': t.altitude,
        'description': t.description,
        'assigned_staff_id': t.assigned_staff_id,
        'assigned_staff_name': t.assigned_staff.full_name if t.assigned_staff else None
    }

def normalize_trek_data(data):
    return {
        'trek_name': data.get('trek_name'),
        'location': data.get('location'),
        'difficulty': data.get('difficulty'),
        'duration_days': int(data.get('duration_days')),
        'total_slots': int(data.get('total_slots')),
        'available_slots': int(data.get('available_slots')),
        'status': data.get('status'),
        'start_date': data.get('start_date') or None,
        'end_date': data.get('end_date') or None,
        'altitude': data.get('altitude') or None,
        'description': data.get('description') or None,
        'assigned_staff_id': int(data['assigned_staff_id']) if data.get('assigned_staff_id') else None,
    }
