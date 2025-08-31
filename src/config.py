# Configuration settings for the Flask application

import os

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_default_secret_key'
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1']
    TESTING = os.environ.get('TESTING', 'False').lower() in ['true', '1']
    DATABASE_URI = os.environ.get('DATABASE_URI') or 'mssql+pymssql://sa:Phuc070202022@127.0.0.1:1433/DB_TEST'
    CORS_HEADERS = 'Content-Type'
    
    # MoMo Payment Gateway Configuration
    MOMO_PARTNER_CODE = os.environ.get('MOMO_PARTNER_CODE') or 'MOMO'
    MOMO_ACCESS_KEY = os.environ.get('MOMO_ACCESS_KEY') or 'F8BBA842ECF85'
    MOMO_SECRET_KEY = os.environ.get('MOMO_SECRET_KEY') or 'K951B6PE1waDMi640xX08PD3vg6EkVlz' # Thay thế bằng Secret Key thực tế của bạn
    MOMO_API_ENDPOINT = os.environ.get('MOMO_API_ENDPOINT') or 'https://test-payment.momo.vn/v2/gateway/api/create'
    MOMO_QUERY_URL = "https://test-payment.momo.vn/v2/gateway/api/query"
    MOMO_RETURN_URL = os.environ.get('MOMO_RETURN_URL') or 'http://localhost:6868/api/payments/momo/return'
    MOMO_NOTIFY_URL = os.environ.get('MOMO_NOTIFY_URL') or 'http://localhost:6868/api/payments/momo/notify'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DATABASE_URI = os.environ.get('DATABASE_URI') or 'mssql+pymssql://sa:Phuc070202022@127.0.0.1:1433/DB_TEST'


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE_URI = os.environ.get('DATABASE_URI') or 'mssql+pymssql://sa:Phuc070202022@127.0.0.1:1433/DB_TEST'


class ProductionConfig(Config):
    """Production configuration."""
    DATABASE_URI = os.environ.get('DATABASE_URI') or 'mssql+pymssql://sa:Phuc070202022@127.0.0.1:1433/DB_TEST'

    
template = {
    "swagger": "2.0",
    "info": {
        "title": "Ticket API",
        "description": "API for managing tickets and users",
        "version": "1.0.0"
    },
    "basePath": "/",
    "schemes": [
        "http",
        "https"
    ],
    "consumes": [
        "application/json"
    ],
    "produces": [
        "application/json"
    ]
}
class SwaggerConfig:
    """Swagger configuration."""
    template = {
        "swagger": "2.0",
        "info": {
            "title": "Ticket API",
            "description": "API for managing tickets and users",
            "version": "1.0.0"
        },
        "basePath": "/",
        "schemes": [
            "http",
            "https"
        ],
        "consumes": [
            "application/json"
        ],
        "produces": [
            "application/json"
        ]
    }

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
        "specs_route": "/docs"
    }