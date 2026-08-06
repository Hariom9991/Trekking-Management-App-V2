from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

from .user import User
from .trek import Trek
from .booking import Booking
from .notification import Notification
from .export_job import ExportJob
