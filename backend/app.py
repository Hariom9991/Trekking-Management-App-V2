from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db, login_manager
from models.user import User
from routes.auth_routes import auth
from routes.admin_routes import admin
from routes.staff_routes import staff
from routes.user_routes import user
from services.seed_service import seed_admin, seed_treks
from extensions import cache, celery_app
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['EXPORT_DIR'] = os.path.join(app.root_path, 'export')

    CORS(
        app,
        supports_credentials=True,
        origins=[
            'http://localhost:5173',
            'http://127.0.0.1:5173',
            'http://localhost:5174',
            'http://127.0.0.1:5174',
            'http://localhost:4173',
            'http://127.0.0.1:4173',
        ],
    )

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = None
    login_manager.session_protection = None

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({'error': 'Unauthorized. Please login again.'}), 401

    try:
        cache.init_app(app)
    except Exception:
        cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})

    celery_app.conf.update(
        broker_url=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
        result_backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
        timezone=app.config.get('CELERY_TIMEZONE', 'Asia/Kolkata'),
    )

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(staff)
    app.register_blueprint(user)

    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok'})

    @app.route('/api/debug/session')
    def debug_session():
        from flask_login import current_user
        return jsonify({
            'authenticated': bool(getattr(current_user, 'is_authenticated', False)),
            'user_id': getattr(current_user, 'id', None),
            'role': getattr(current_user, 'role', None),
        })

    with app.app_context():
        db.create_all()
        seed_admin()   

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)