from flask import Blueprint, request, jsonify
from flask_login import current_user
from models import db
from models.trek import Trek
from models.booking import Booking
from utils.auth import role_required
from extensions import cache

staff = Blueprint('staff', __name__, url_prefix='/api/staff')

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
        'participants': len([b for b in t.bookings if b.status in ['booked', 'completed']])
    }

@staff.get('/dashboard')
@role_required('staff')
def dashboard():
    treks = Trek.query.filter_by(assigned_staff_id=current_user.id).all()
    stats = {
        'assigned_treks': len(treks),
        'participants': sum(len([b for b in t.bookings if b.status in ['booked', 'completed']]) for t in treks),
        'ongoing': len([t for t in treks if t.status == 'ongoing'])
    }
    return jsonify({'stats': stats, 'treks': [serialize_trek(t) for t in treks]})

@staff.get('/treks')
@role_required('staff')
def my_treks():
    treks = Trek.query.filter_by(assigned_staff_id=current_user.id).all()
    return jsonify({'items': [serialize_trek(t) for t in treks]})

@staff.get('/treks/<int:trek_id>')
@role_required('staff')
def trek_detail(trek_id):
    trek = Trek.query.filter_by(id=trek_id, assigned_staff_id=current_user.id).first()
    if not trek:
        return jsonify({'error': 'Trek not found or not assigned.'}), 404
    return jsonify(serialize_trek(trek))

@staff.put('/treks/<int:trek_id>')
@role_required('staff')
def update_trek(trek_id):
    trek = Trek.query.filter_by(id=trek_id, assigned_staff_id=current_user.id).first()
    if not trek:
        return jsonify({'error': 'Trek not found or not assigned.'}), 404
    data = request.get_json() or {}
    if 'available_slots' in data:
        value = int(data['available_slots'])
        if value < 0 or value > trek.total_slots:
            return jsonify({'error': 'Available slots out of range.'}), 400
        trek.available_slots = value
    if 'status' in data:
        if data['status'] not in ['open', 'closed', 'ongoing', 'completed']:
            return jsonify({'error': 'Invalid status.'}), 400
        trek.status = data['status']
    db.session.commit()
    try:
        cache.clear()
    except Exception:
        pass
    return jsonify({'message': 'Trek updated.'})

@staff.get('/treks/<int:trek_id>/participants')
@role_required('staff')
def participants(trek_id):
    trek = Trek.query.filter_by(id=trek_id, assigned_staff_id=current_user.id).first()
    if not trek:
        return jsonify({'error': 'Trek not found or not assigned.'}), 404
    items = [{'id': b.user.id, 'full_name': b.user.full_name, 'email': b.user.email, 'status': b.status} for b in trek.bookings]
    return jsonify({'items': items})
