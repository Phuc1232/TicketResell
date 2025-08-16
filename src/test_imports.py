#!/usr/bin/env python3
"""
Test script to check if all imports work correctly
"""

def test_imports():
    print("🔍 Testing imports...")
    
    try:
        # Test basic Flask imports
        print("✅ Testing Flask imports...")
        from flask import Flask, Blueprint, request, jsonify
        from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
        
        # Test Marshmallow imports
        print("✅ Testing Marshmallow imports...")
        from marshmallow import Schema, fields, validate
        
        # Test API controllers
        print("✅ Testing API controllers...")
        from api.controllers.ticket_controller import bp as ticket_bp
        from api.controllers.user_controller import bp as user_bp
        from api.controllers.auth_controller import bp as auth_bp
        from api.controllers.transaction_controller import bp as transaction_bp
        from api.controllers.chat_controller import bp as chat_bp
        from api.controllers.notification_controller import bp as notification_bp
        from api.controllers.feedback_controller import bp as feedback_bp
        
        # Test API routes
        print("✅ Testing API routes...")
        from api.routes import register_routes
        
        # Test Swagger
        print("✅ Testing Swagger imports...")
        from api.swagger import spec
        
        # Test schemas
        print("✅ Testing schema imports...")
        from api.schemas.ticket import TicketRequestSchema, TicketResponseSchema
        from api.schemas.user import UserLoginSchema, UserRegisterSchema
        
        # Test infrastructure
        print("✅ Testing infrastructure imports...")
        from infrastructure.databases import init_db
        from infrastructure.models.Ticket_model import TicketModel
        from infrastructure.models.user_model import UserModel
        from infrastructure.models.transaction_model import TransactionModel
        from infrastructure.models.message_model import MessageModel
        from infrastructure.models.notification_model import NotificationModel
        from infrastructure.models.feedback_model import UserFeedbackModel, TicketFeedbackModel
        
        # Test repositories
        print("✅ Testing repository imports...")
        from infrastructure.repositories.ticket_repository import TicketRepository
        from infrastructure.repositories.user_repository import UserRepository
        from infrastructure.repositories.transaction_repository import TransactionRepository
        from infrastructure.repositories.message_repository import MessageRepository
        from infrastructure.repositories.notification_repository import NotificationRepository
        from infrastructure.repositories.feedback_repository import FeedbackRepository
        
        # Test services
        print("✅ Testing service imports...")
        from services.ticket_service import TicketService
        from services.user_service import UserService
        from services.transaction_service import TransactionService
        from services.chat_service import ChatService
        from services.notification_service import NotificationService
        from services.feedback_service import FeedbackService
        
        # Test domain models
        print("✅ Testing domain model imports...")
        from domain.models.ticket import Ticket
        from domain.models.user import User
        from domain.models.transaction import Transaction
        from domain.models.message import Message
        from domain.models.notification import Notification
        from domain.models.feedback import Feedback, TicketFeedback
        
        # Test domain repository interfaces
        print("✅ Testing domain repository interfaces...")
        from domain.models.itticket_repository import ITicketRepository
        from domain.models.iuser_repository import IUserRepository
        from domain.models.itransaction_repository import ITransactionRepository
        from domain.models.imessage_repository import IMessageRepository
        from domain.models.inotification_repository import INotificationRepository
        from domain.models.ifeedback_repository import IFeedbackRepository
        
        # Test dependency container
        print("✅ Testing dependency container...")
        from dependency_container import DependencyContainer
        
        print("🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_app_creation():
    print("\n🔍 Testing app creation...")
    
    try:
        from app import create_app
        app = create_app()
        print("✅ App creation successful!")
        
        # Test if all blueprints are registered
        registered_blueprints = list(app.blueprints.keys())
        print(f"✅ Registered blueprints: {registered_blueprints}")
        
        # Test if routes are registered
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.methods} {rule.rule}")
        
        print(f"✅ Found {len(routes)} routes")
        return True
        
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

def test_dependency_container():
    print("\n🔍 Testing dependency container...")
    
    try:
        from dependency_container import DependencyContainer
        container = DependencyContainer()
        
        # Test all services
        services = [
            container.get_ticket_service(),
            container.get_user_service(),
            container.get_transaction_service(),
            container.get_chat_service(),
            container.get_notification_service(),
            container.get_feedback_service()
        ]
        
        print(f"✅ Dependency container created successfully with {len(services)} services")
        return True
        
    except Exception as e:
        print(f"❌ Dependency container error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting import tests...\n")
    
    imports_ok = test_imports()
    app_ok = test_app_creation()
    container_ok = test_dependency_container()
    
    print("\n" + "="*50)
    if imports_ok and app_ok and container_ok:
        print("🎉 All tests passed! Ready to run the application.")
        print("\nTo start the application, run:")
        print("python app.py")
        print("\nThen visit:")
        print("http://localhost:6868/docs")
    else:
        print("❌ Some tests failed. Please check the errors above.")
