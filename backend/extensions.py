from flask_caching import Cache
from celery import Celery
import os

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
celery_app = Celery(
    __name__,
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
)
celery_app.conf.update(
    broker_connection_retry_on_startup=True,
    timezone=os.getenv('CELERY_TIMEZONE', 'Asia/Kolkata'),
    enable_utc=False
)
