from infrastructure.databases.mssql import init_mssql
from infrastructure.models import user_model,message_model,transaction_model,role_model,Ticket_model,feedback_model,payment_model,earning_model,support_model

def init_db(app):
    init_mssql(app)

from infrastructure.databases.mssql import Base