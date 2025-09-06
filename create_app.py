from flask import Flask
from .config import Config
from .api.middleware import setup_middleware
from .api.routes import register_routes
from .infrastructure.databases import init_db
from .app_logging import setup_logging
from flask_jwt_extended import JWTManager
from .cors import init_cors
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["JWT_SECRET_KEY"] = "super-secret"  # đổi thành key bảo mật
    JWTManager(app)
    setup_logging(app)
    init_db(app)
    init_cors(app)  # Khởi tạo CORS
    setup_middleware(app)
    register_routes(app)

    return app