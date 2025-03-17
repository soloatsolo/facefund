from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os
from .services.logger import setup_logger

# Initialize SQLAlchemy and logger
db = SQLAlchemy()
logger = setup_logger()

def create_app(test_config=None):
    # Load environment variables from .env file
    load_dotenv()
    
    # Create Flask app
    app = Flask(__name__)
    CORS(app)
    
    # Configure the app
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
            SQLALCHEMY_DATABASE_URI=os.environ.get(
                'DATABASE_URL',
                'sqlite:///' + os.path.join(app.instance_path, 'faces.db')
            ),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            UPLOAD_FOLDER=os.environ.get('UPLOAD_FOLDER', os.path.join(app.static_folder, 'uploads')),
            MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max file size
        )
    else:
        app.config.update(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Ensure upload folder exists
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        pass

    # Initialize database
    db.init_app(app)

    # Register blueprints
    from .routes import face_recognition_bp
    app.register_blueprint(face_recognition_bp)

    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info('Application initialized successfully')

    return app