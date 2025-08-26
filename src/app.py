from flask import Flask, jsonify
from api.swagger import spec
from api.middleware import middleware
from api.responses import success_response
from infrastructure.databases import init_db
from config import Config
from flasgger import Swagger
from config import SwaggerConfig
from flask_swagger_ui import get_swaggerui_blueprint
from api.routes import register_routes
from cors import init_cors
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print(".env file loaded successfully")
except ImportError:
    print("WARNING: python-dotenv not installed. Using system environment variables only.")
except Exception as e:
    print(f"WARNING: Error loading .env file: {e}")
from flask_jwt_extended import JWTManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _seed_admin_user():
    """
    Seed admin user sau khi database được khởi tạo
    """
    try:
        logger.info("Starting admin seed process...")

        # Import dependencies (lazy import để tránh circular imports)
        from database.seed_admin import seed_default_admin
        from infrastructure.repositories.user_repository import UserRepository
        from infrastructure.databases.mssql import session

        # Create repository
        user_repository = UserRepository(session)

        # Run seed
        success = seed_default_admin(user_repository)

        if success:
            logger.info("Admin seed process completed successfully!")
        else:
            logger.warning("Admin seed process completed with warnings")

    except Exception as e:
        logger.error(f"Admin seed process failed: {e}")
        # Không crash app nếu seed thất bại
        logger.warning("Application will continue without admin seed")


def create_app():
    app = Flask(__name__)
    Swagger(app)

    app.config["JWT_SECRET_KEY"] = "super-secret"  # đổi thành key bảo mật
    JWTManager(app)
    
    # Khởi tạo CORS
    init_cors(app)
    
    # Đăng ký tất cả routes từ routes.py
    register_routes(app)
    
    # Thêm Swagger UI blueprint
    SWAGGER_URL = '/docs'
    API_URL = '/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "TicketResell API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    try:
        init_db(app)

        # Seed admin user after database initialization
        _seed_admin_user()

    except Exception as e:
        print(f"Error initializing database: {e}")

    # Register middleware
    middleware(app)

    # Register routes for Swagger
    with app.test_request_context():
        for rule in app.url_map.iter_rules():
            # Thêm tất cả endpoints cho Swagger
            if rule.endpoint.startswith(('ticket.', 'user.', 'auth.', 'admin.', 'transactions.', 'chat.','feedback.', 'payment.', 'earning.', 'support.')):
                view_func = app.view_functions[rule.endpoint]
                print(f"Adding path: {rule.rule} -> {view_func}")
                spec.path(view=view_func)

    @app.route("/swagger.json")
    def swagger_json():
        return jsonify(spec.to_dict())

    @app.route("/health")
    def health_check():
        return jsonify({"status": "healthy", "message": "TicketResell API is running"})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=6868, debug=True)