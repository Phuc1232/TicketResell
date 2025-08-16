from infrastructure.databases.mssql import init_mssql
from infrastructure.models import user_model,role_model,Mess_model,feedback_model,Ticket_model,Trans_model,Noti_model

def init_db(app):
    init_mssql(app)
    
from infrastructure.databases.mssql import Base