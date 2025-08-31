from api.controllers.ticket_controller import bp as ticket_bp
from api.controllers.user_controller import bp as user_bp
from api.controllers.auth_controller import bp as auth_bp
from api.controllers.admin_controller import bp as admin_bp
from api.controllers.transaction_controller import bp as transaction_bp
from api.controllers.chat_controller import bp as chat_bp
from api.controllers.feedback_controller import bp as feedback_bp
from api.controllers.payment_controller import bp as payment_bp
from api.controllers.earning_controller import bp as earning_bp
from api.controllers.support_controller import bp as support_bp


def register_routes(app):
    app.register_blueprint(ticket_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(earning_bp)
    app.register_blueprint(support_bp)
