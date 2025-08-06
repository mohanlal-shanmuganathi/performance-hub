from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger
import os

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 
        'sqlite:///performance.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # CORS configuration for production
    cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
    CORS(app, origins=cors_origins)
    
    jwt.init_app(app)
    
    # Swagger configuration
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }
    swagger = Swagger(app, config=swagger_config)
    
    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.employees import employees_bp
    from app.blueprints.goals import goals_bp
    from app.blueprints.reviews import reviews_bp
    from app.blueprints.analytics import analytics_bp
    from app.blueprints.skills import skills_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(employees_bp, url_prefix='/api/employees')
    app.register_blueprint(goals_bp, url_prefix='/api/goals')
    app.register_blueprint(reviews_bp, url_prefix='/api/reviews')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(skills_bp, url_prefix='/api/skills')
    
    # Add root route
    @app.route('/')
    def index():
        return {
            'message': 'Employee Performance Management System API',
            'version': '1.0.0',
            'endpoints': {
                'api_docs': '/docs/',
                'auth': '/api/auth/',
                'employees': '/api/employees/',
                'goals': '/api/goals/',
                'reviews': '/api/reviews/',
                'analytics': '/api/analytics/'
            }
        }
    
    return app