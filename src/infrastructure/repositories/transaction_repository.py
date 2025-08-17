from typing import List, Optional
from domain.models.transaction import Transaction
from domain.models.itransaction_repository import ITransactionRepository
from infrastructure.models.transaction_model import TransactionModel
from datetime import datetime

class TransactionRepository(ITransactionRepository):
    def __init__(self, session=None):
        if session is None:
            from infrastructure.databases.mssql import session as default_session
            self.session = default_session
        else:
            self.session = session
    def add(self, transaction: Transaction) -> Transaction:
        model = TransactionModel(
            TicketID=transaction.TicketID,
            BuyerID=transaction.BuyerID,
            SellerID=transaction.SellerID,
            Amount=transaction.Amount,
            PaymentMethod=transaction.PaymentMethod,
            Status=transaction.Status,
            PaymentTransactionID=transaction.PaymentTransactionID,
            CreatedAt=transaction.CreatedAt,
            UpdatedAt=transaction.UpdatedAt
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)

    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        model = self.session.query(TransactionModel).filter(TransactionModel.TransactionID == transaction_id).first()
        return self._to_domain(model) if model else None
    
    def get_by_ticket_id(self, ticket_id: int) -> List[Transaction]:
        models = self.session.query(TransactionModel).filter(TransactionModel.TicketID == ticket_id).all()
        return [self._to_domain(model) for model in models]

    def get_by_user_id(self, user_id: int) -> List[Transaction]:
        models = self.session.query(TransactionModel).filter(
            (TransactionModel.BuyerID == user_id) | (TransactionModel.SellerID == user_id)
        ).all()
        return [self._to_domain(model) for model in models]

    def update(self, transaction: Transaction) -> Transaction:
        model = self.session.query(TransactionModel).filter(TransactionModel.TransactionID == transaction.TransactionID).first()
        if model:
            model.TicketID = transaction.TicketID
            model.BuyerID = transaction.BuyerID
            model.SellerID = transaction.SellerID
            model.Amount = transaction.Amount
            model.PaymentMethod = transaction.PaymentMethod
            model.Status = transaction.Status
            model.PaymentTransactionID = transaction.PaymentTransactionID
            model.UpdatedAt = datetime.now()
            self.session.commit()
            self.session.refresh(model)
            return self._to_domain(model)
        return transaction
    
    def delete(self, transaction_id: int) -> bool:
        model = self.session.query(TransactionModel).filter(TransactionModel.TransactionID == transaction_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False

    def list(self) -> List[Transaction]:
        models = self.session.query(TransactionModel).all()
        return [self._to_domain(model) for model in models]
    
    def _to_domain(self, model: TransactionModel) -> Transaction:
        return Transaction(
            TransactionID=model.TransactionID,
            TicketID=model.TicketID,
            BuyerID=model.BuyerID,
            SellerID=model.SellerID,
            Amount=model.Amount,
            PaymentMethod=model.PaymentMethod,
            Status=model.Status,
            PaymentTransactionID=model.PaymentTransactionID,
            CreatedAt=model.CreatedAt,
            UpdatedAt=model.UpdatedAt
        )
