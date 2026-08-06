import requests
from models import db
from models.trek import Trek
from models.booking import Booking
from models.notification import Notification
from models.user import User
from services.mail_service import send_html_email


def create_daily_reminders(app):
    count = 0

    webhook = app.config.get('GOOGLE_CHAT_WEBHOOK')
    upcoming = Trek.query.filter(
        Trek.status.in_(['approved', 'open', 'ongoing'])
    ).all()

    for trek in upcoming:
        for booking in trek.bookings:
            if booking.status != 'booked':
                continue

            user = User.query.get(booking.user_id)
            if not user:
                continue

            # Notification message
            message = (
                f'Reminder: Upcoming trek {trek.trek_name} at {trek.location}. '
                f'Start: {trek.start_date or "TBA"}.'
            )

            # Store notification in DB
            db.session.add(Notification(user_id=booking.user_id, message=message))

            # Send Google Chat message if webhook is configured
            if webhook:
                try:
                    requests.post(webhook, json={'text': message}, timeout=5)
                except Exception:
                    # ignore Google Chat failures, do not break task
                    pass

            # Send email via Mailpit if user has email
            if getattr(user, "email", None):
                # Pick a safe display name (adjust field names to your model)
                display_name = (
                    getattr(user, "full_name", None)
                    or getattr(user, "username", None)
                    or user.email
                )

                html = f"""
                <h2>Trek Reminder</h2>
                <p>Hello {display_name},</p>
                <p>This is a reminder that your trek <strong>{trek.trek_name}</strong>
                at <strong>{trek.location}</strong> is scheduled to start on
                <strong>{trek.start_date or "TBA"}</strong>.</p>
                <p>Please arrive on time and carry your essentials.</p>
                """

                try:
                    send_html_email(
                        app,
                        to_email=user.email,
                        subject=f'Reminder: {trek.trek_name} starts soon',
                        html=html
                    )
                except Exception:
                    # do not break all reminders if one email fails
                    pass

            count += 1

    db.session.commit()
    return count