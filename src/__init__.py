import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from src.constants.http_status_codes import (
    HTTP_400_BAD_REQUEST, 
    HTTP_404_NOT_FOUND, 
    HTTP_405_METHOD_NOT_ALLOWED, 
    HTTP_500_ERROR_SERVER)
from src.models.model import db
from src.handlers.user import user
from src.handlers.task import task
from src.handlers.delivery import delivery
from datetime import timedelta 


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    if test_config is None:
        app.config.from_mapping(
            FLASK_ENV = os.environ.get('FLASK_ENV'),
            SECRET_KEY = os.environ.get('SECRET_KEY'),
            JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY'),
            MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE_URI'),
            JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours= int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES'))),
            JWT_REFRESH_TOKEN_EXPIRES = timedelta(days= int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES'))))
    else:
        app.config.from_mapping(test_config)
    
    JWTManager(app)
    db.app = app
    db.init_app(app)
    app.register_blueprint(user)
    app.register_blueprint(task)
    app.register_blueprint(delivery)
    
    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(error):
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND
    
    @app.errorhandler(HTTP_400_BAD_REQUEST)
    def handle_404(error):
        return jsonify({'error': 'Bad request'}), HTTP_400_BAD_REQUEST
    
    @app.errorhandler(HTTP_405_METHOD_NOT_ALLOWED)
    def handle_404(error):
        return jsonify({'error': 'Bad request'}), HTTP_405_METHOD_NOT_ALLOWED
    
    @app.errorhandler(HTTP_500_ERROR_SERVER)
    def handle_500(error):
        return jsonify({
            'error': 'Somthing went wrong, we are working on it'
            }), HTTP_500_ERROR_SERVER
    
    return app
