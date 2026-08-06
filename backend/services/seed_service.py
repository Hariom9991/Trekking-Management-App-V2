from models import db
from models.user import User
from models.trek import Trek


def seed_admin():
    admin = User.query.filter_by(email='admin@tma.com').first()
    if not admin:
        admin = User(
            full_name='System Admin',
            email='admin@tma.com',
            role='admin',
            status='active',
            contact_number='9999999999'
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()


def seed_treks():
    return