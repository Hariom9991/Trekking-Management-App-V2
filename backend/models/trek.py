from . import db

class Trek(db.Model):
    __tablename__ = 'treks'
    id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    altitude = db.Column(db.String(50))
    description = db.Column(db.Text)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    assigned_staff = db.relationship('User', back_populates='managed_treks', foreign_keys=[assigned_staff_id])
    bookings = db.relationship('Booking', back_populates='trek', cascade='all, delete-orphan')
