import os
import io
import csv
from celery.schedules import crontab

from app import create_app
from extensions import celery_app
from services.reminder_service import create_daily_reminders
from services.report_service import build_monthly_html
from services.mail_service import send_html_email
from models import db
from models.booking import Booking
from models.trek import Trek
from models.export_job import ExportJob
from models.user import User

app = create_app()

celery_app.conf.beat_schedule = {
    'daily-reminder-0700': {
        'task': 'tasks.daily_reminder',
        'schedule': crontab(hour=7, minute=0)
    },
    'monthly-report-first-day-midnight': {
        'task': 'tasks.monthly_report',
        'schedule': crontab(day_of_month=1, hour=0, minute=0)
    },
}


@celery_app.task(name='tasks.daily_reminder')
def daily_reminder():
    with app.app_context():
        return f'Daily reminders created: {create_daily_reminders(app)}'


@celery_app.task(name='tasks.monthly_report')
def monthly_report():
    with app.app_context():
        html = build_monthly_html()

        report_dir = os.path.join(app.root_path, 'reports')
        os.makedirs(report_dir, exist_ok=True)

        report_path = os.path.join(report_dir, 'monthly_report.html')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)

        try:
            send_html_email(
                app,
                to_email='admin@tma.com',
                subject='Monthly Trekking Activity Report',
                html=html
            )
        except Exception as e:
            return f'Report saved at {report_path}, mail failed: {str(e)}'

        return f'Report saved at {report_path}'


@celery_app.task(name='tasks.export_history_csv', bind=True)
def export_history_csv(self, user_id: int):
    with app.app_context():
        job = ExportJob.query.filter_by(task_id=self.request.id).first()
        try:
            user = db.session.get(User, user_id)
            if not user:
                if job:
                    job.status = 'failed'
                    db.session.commit()
                return ''

            bookings = (
                Booking.query
                .filter_by(user_id=user_id)
                .order_by(Booking.booking_date.desc())
                .all()
            )

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(
                ['User ID', 'Trek Name', 'Location', 'Booking Status', 'Booking Date', 'Payment Status']
            )

            for b in bookings:
                trek = db.session.get(Trek, b.trek_id)
                writer.writerow([
                    user_id,
                    trek.trek_name if trek else '',
                    trek.location if trek else '',
                    b.status,
                    b.booking_date.strftime('%Y-%m-%d') if b.booking_date else '',
                    b.payment_status
                ])

            export_dir = os.path.join(app.root_path, 'export')
            os.makedirs(export_dir, exist_ok=True)

            file_name = f'history_{user_id}_{self.request.id}.csv'
            path = os.path.join(export_dir, file_name)

            with open(path, 'w', encoding='utf-8', newline='') as f:
                f.write(output.getvalue())

            if job:
                job.file_name = file_name
                job.status = 'finished'
                db.session.commit()

            return path

        except Exception:
            if job:
                job.status = 'failed'
                db.session.commit()
            raise