from src.api.controllers.ticket_controller import bp as ticket_bp
from src.api.controllers.user_controller import bp as user_bp
def register_routes(app):
    app.register_blueprint(ticket_bp)
    app.register_blueprint(user_bp)