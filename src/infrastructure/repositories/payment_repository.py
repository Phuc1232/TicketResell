from typing import List, Optional
from domain.models.payment import Payment
from domain.models.ipayment_repository import IPaymentRepository
from infrastructure.models.payment_model import PaymentModel
from datetime import datetime

class PaymentRepository(IPaymentRepository):
    def __init__(self, session=None):
        if session is None:
            from infrastructure.databases.mssql import session as default_session
            self.session = default_session
        else:
            self.session = session

    def add(self, payment: Payment) -> Payment:
        model = PaymentModel(
            Methods=payment.Methods,
            Status=payment.Status,
            Paid_at=payment.Paid_at,
            amount=payment.amount,
            UserID=payment.UserID,
            Title=payment.Title,
            TransactionID=payment.TransactionID
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)
    
    def get_by_id(self, payment_id: int) -> Optional[Payment]:
        model = self.session.query(PaymentModel).filter(PaymentModel.PaymentID == payment_id).first()
        return self._to_domain(model) if model else None
    
    def get_by_user_id(self, user_id: int) -> List[Payment]:
        models = self.session.query(PaymentModel).filter(PaymentModel.UserID == user_id).all()
        return [self._to_domain(model) for model in models]
    
    def get_by_transaction_id(self, transaction_id: int) -> Optional[Payment]:
        model = self.session.query(PaymentModel).filter(PaymentModel.TransactionID == transaction_id).first()
        return self._to_domain(model) if model else None
    
    def update(self, payment: Payment) -> Payment:
        model = self.session.query(PaymentModel).filter(PaymentModel.PaymentID == payment.PaymentID).first()
        if model:
            model.Methods = payment.Methods
            model.Status = payment.Status
            model.Paid_at = payment.Paid_at
            model.amount = payment.amount
            model.UserID = payment.UserID
            model.Title = payment.Title
            model.TransactionID = payment.TransactionID
            self.session.commit()
            self.session.refresh(model)
            return self._to_domain(model)
        return None
    
    def delete(self, payment_id: int) -> bool:
        model = self.session.query(PaymentModel).filter(PaymentModel.PaymentID == payment_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False
    
    def get_by_status(self, status: str) -> List[Payment]:
        models = self.session.query(PaymentModel).filter(PaymentModel.Status == status).all()
        return [self._to_domain(model) for model in models]

    def get_user_payments_paginated(self, user_id: int, limit: int, offset: int) -> List[Payment]:
        models = (self.session.query(PaymentModel)
                 .filter(PaymentModel.UserID == user_id)
                 .order_by(PaymentModel.PaymentID.desc())
                 .limit(limit)
                 .offset(offset)
                 .all())
        return [self._to_domain(model) for model in models]

    def get_user_payments_count(self, user_id: int) -> int:
        return self.session.query(PaymentModel).filter(PaymentModel.UserID == user_id).count()
    
    def _to_domain(self, model: PaymentModel) -> Payment:
        return Payment(
            PaymentID=model.PaymentID,
            Methods=model.Methods,
            Status=model.Status,
            Paid_at=model.Paid_at,
            amount=model.amount,
            UserID=model.UserID,
            Title=model.Title,
            TransactionID=model.TransactionID
        )
