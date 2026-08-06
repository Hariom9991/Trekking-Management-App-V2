from datetime import datetime
from . import db

class Booking(db.Model):
    __tablename__ = 'bookings'
    __table_args__ = (db.UniqueConstraint('user_id', 'trek_id', name='uq_user_trek_booking'),)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='booked')
    payment_status = db.Column(db.String(30), nullable=False, default='pending')
    payment_method = db.Column(db.String(30))
    transaction_id = db.Column(db.String(120))

    user = db.relationship('User', back_populates='bookings')
    trek = db.relationship('Trek', back_populates='bookings')
