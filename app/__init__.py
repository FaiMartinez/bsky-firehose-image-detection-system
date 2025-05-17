from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max
    app.secret_key = os.urandom(24)

    from .routes import main
    app.register_blueprint(main)

    return app

UPLOAD_FOLDER = 'static/uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)    
# This is the main application factory function. It creates and configures the Flask app.
# It loads environment variables, sets up the upload folder, and registers the main blueprint.