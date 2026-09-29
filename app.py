import os
from flask import Flask, render_template, send_from_directory
from config import Config
from database.database import db, login_manager
from database.models import User

# Import Blueprints
from routes.auth import auth_bp
from routes.lab import lab_bp
from routes.patient import patient_bp
from routes.hospital import hospital_bp
from routes.blockchain import blockchain_bp
from routes.analytics import analytics_bp

def create_app(test_config=None):
    app = Flask(__name__)
    if test_config:
        app.config.from_object(Config)
        app.config.update(test_config)
    else:
        app.config.from_object(Config)


    # Ensure Upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # Ensure Instance folder exists for SQLite
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(lab_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(hospital_bp)
    app.register_blueprint(blockchain_bp)
    app.register_blueprint(analytics_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/downloads/<path:filename>')
    def download_file(filename):
        return send_from_directory('downloads', filename, as_attachment=True)


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Error Handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template(
            'error.html',
            error_title="Forbidden Access",
            error_message="You do not have the required permissions to view this resource."
        ), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template(
            'error.html',
            error_title="Page Not Found",
            error_message="The URL you are looking for does not exist on the LABCHAIN network."
        ), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template(
            'error.html',
            error_title="Internal System Error",
            error_message="An unexpected error occurred in the LABCHAIN backend."
        ), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
