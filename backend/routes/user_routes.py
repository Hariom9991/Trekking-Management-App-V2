import os
import io
import csv

from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_login import current_user

from models import db
from models.trek import Trek
from models.booking import Booking
from models.notification import Notification
from models.export_job import ExportJob
from utils.auth import role_required
from extensions import cache, celery_app


user = Blueprint('user', __name__, url_prefix='/api/user')


@user.get('/dashboard')
@role_required('user')
def dashboard():
    bookings = Booking.query.filter_by(user_id=current_user.id) \
        .order_by(Booking.booking_date.desc()).all()

    stats = {
        'available_treks': Trek.query.filter_by(status='open').count(),
        'my_bookings': len(bookings),
        'completed_treks': len([b for b in bookings if b.status == 'completed'])
    }

    return jsonify({
        'stats': stats,
        'bookings': [
            {
                'id': b.id,
                'trek_name': b.trek.trek_name if b.trek else '',
                'status': b.status,
                'payment_status': b.payment_status
            }
            for b in bookings[:10]
        ]
    })


@user.get('/treks')
@role_required('user')
@cache.cached(timeout=60, query_string=True)
def treks():
    q = request.args.get('q', '').strip().lower()
    difficulty = request.args.get('difficulty', '').strip()
    location = request.args.get('location', '').strip().lower()
    duration = request.args.get('duration', '').strip()

    query = Trek.query.filter(
        Trek.status.in_(['approved', 'open', 'ongoing', 'closed', 'completed'])
    )

    if q:
        query = query.filter(
            (Trek.trek_name.ilike(f'%{q}%')) |
            (Trek.location.ilike(f'%{q}%'))
        )

    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    if location:
        query = query.filter(Trek.location.ilike(f'%{location}%'))

    if duration.isdigit():
        query = query.filter_by(duration_days=int(duration))

    items = query.order_by(Trek.id.desc()).all()
    return jsonify({'items': [serialize_trek(t) for t in items]})


@user.get('/bookings')
@role_required('user')
def bookings():
    items = Booking.query.filter_by(user_id=current_user.id) \
        .order_by(Booking.booking_date.desc()).all()
    return jsonify({'items': [serialize_booking(b) for b in items]})


@user.post('/bookings')
@role_required('user')
def book():
    data = request.get_json() or {}

    trek = db.session.get(Trek, data.get('trek_id'))
    if not trek:
        return jsonify({'error': 'Trek not found.'}), 404

    if trek.status != 'open':
        return jsonify({'error': 'Booking allowed only for open treks.'}), 400

    if trek.available_slots <= 0:
        return jsonify({'error': 'No slots available.'}), 400

    existing = Booking.query.filter_by(
        user_id=current_user.id,
        trek_id=trek.id
    ).first()

    if existing and existing.status != 'cancelled':
        return jsonify({'error': 'Duplicate booking not allowed.'}), 400

    payment_method = data.get('payment_method')
    payment_status = data.get('payment_status', 'pending')
    transaction_id = data.get('transaction_id')

    if not payment_method or not transaction_id:
        return jsonify({'error': 'Payment method and transaction ID are required.'}), 400

    if payment_status not in ['simulated-paid', 'failed', 'pending']:
        return jsonify({'error': 'Invalid payment status.'}), 400

    if payment_status == 'failed':
        return jsonify({'error': 'Payment failed. Booking not created.'}), 400

    booking = Booking(
        user_id=current_user.id,
        trek_id=trek.id,
        status='booked',
        payment_status=payment_status,
        payment_method=payment_method,
        transaction_id=transaction_id
    )

    trek.available_slots -= 1
    db.session.add(booking)
    db.session.add(Notification(
        user_id=current_user.id,
        message=f'Booking confirmed for {trek.trek_name}.'
    ))
    db.session.commit()

    try:
        cache.clear()
    except Exception:
        pass

    return jsonify({'message': 'Booking successful.'}), 201


@user.post('/bookings/<int:booking_id>/cancel')
@role_required('user')
def cancel_booking(booking_id):
    booking = Booking.query.filter_by(
        id=booking_id,
        user_id=current_user.id
    ).first()

    if not booking:
        return jsonify({'error': 'Booking not found.'}), 404

    if booking.status == 'cancelled':
        return jsonify({'error': 'Booking already cancelled.'}), 400

    booking.status = 'cancelled'

    if booking.trek and booking.trek.available_slots < booking.trek.total_slots:
        booking.trek.available_slots += 1

    db.session.add(Notification(
        user_id=current_user.id,
        message=f'Booking cancelled for {booking.trek.trek_name}.'
    ))
    db.session.commit()

    try:
        cache.clear()
    except Exception:
        pass

    return jsonify({'message': 'Booking cancelled.'})


@user.get('/history')
@role_required('user')
def history():
    items = Booking.query.filter_by(user_id=current_user.id) \
        .order_by(Booking.booking_date.desc()).all()
    return jsonify({'items': [serialize_booking(b) for b in items]})


@user.post('/export-history')
@role_required('user')
def export_history():
    file_name = generate_history_csv(current_user.id, sync_suffix='sync')
    task_id = f'sync-{current_user.id}-{file_name}'

    existing = ExportJob.query.filter_by(
        user_id=current_user.id,
        task_id=task_id
    ).first()

    if not existing:
        job = ExportJob(
            user_id=current_user.id,
            task_id=task_id,
            status='finished',
            file_name=file_name
        )
        db.session.add(job)
        db.session.commit()

    return jsonify({
        'task_id': task_id,
        'mode': 'sync'
    })

@user.get('/export-history/status')
@role_required('user')
def export_status():
    task_id = request.args.get('task_id')

    if not task_id:
        return jsonify({'error': 'task_id is required.'}), 400

    job = ExportJob.query.filter_by(
        task_id=task_id,
        user_id=current_user.id
    ).first()

    if not job:
        return jsonify({'error': 'Job not found.'}), 404

    payload = {'status': job.status}

    if job.status == 'finished' and job.file_name:
        payload['download_url'] = f'/api/user/export-history/download/{job.file_name}'

    return jsonify(payload)


@user.get('/export-history/download/<path:file_name>')
@role_required('user')
def download_export(file_name):
    export_dir = current_app.config.get(
        'EXPORT_DIR',
        os.path.join(current_app.root_path, 'export')
    )
    return send_from_directory(export_dir, file_name, as_attachment=True)


@user.get('/profile')
@role_required('user', 'staff')
def profile():
    return jsonify({
        'full_name': current_user.full_name,
        'email': current_user.email,
        'contact_number': current_user.contact_number or ''
    })


@user.put('/profile')
@role_required('user', 'staff')
def update_profile():
    data = request.get_json() or {}
    current_user.full_name = data.get('full_name', current_user.full_name)
    current_user.contact_number = data.get('contact_number', current_user.contact_number)
    db.session.commit()
    return jsonify({'message': 'Profile updated.'})


@user.get('/notifications')
@role_required('user', 'staff')
def notifications():
    items = Notification.query.filter_by(user_id=current_user.id) \
        .order_by(Notification.created_at.desc()).all()

    return jsonify({
        'items': [
            {
                'id': n.id,
                'message': n.message,
                'created_at': n.created_at.isoformat()
            }
            for n in items
        ]
    })


def generate_history_csv(user_id, sync_suffix='manual'):
    bookings = Booking.query.filter_by(user_id=user_id) \
        .order_by(Booking.booking_date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'User ID',
        'Trek Name',
        'Location',
        'Booking Status',
        'Booking Date',
        'Payment Status'
    ])

    for b in bookings:
        trek = db.session.get(Trek, b.trek_id)
        writer.writerow([
            user_id,
            trek.trek_name if trek else '',
            trek.location if trek else '',
            b.status,
            b.booking_date.strftime('%Y-%m-%d'),
            b.payment_status
        ])

    export_dir = current_app.config.get(
        'EXPORT_DIR',
        os.path.join(current_app.root_path, 'export')
    )
    os.makedirs(export_dir, exist_ok=True)

    file_name = f'history_{user_id}_{sync_suffix}.csv'
    file_path = os.path.join(export_dir, file_name)

    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        f.write(output.getvalue())

    return file_name


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
        'end_date': t.end_date
    }


def serialize_booking(b):
    return {
        'id': b.id,
        'trek_name': b.trek.trek_name if b.trek else '',
        'location': b.trek.location if b.trek else '',
        'status': b.status,
        'payment_status': b.payment_status,
        'booking_date': b.booking_date.strftime('%Y-%m-%d')
    }