from typing import List, Optional
from domain.models.support import Support
from domain.models.isupport_repository import ISupportRepository
from domain.models.iuser_repository import IUserRepository
from datetime import datetime

class SupportService:
    def __init__(self, support_repository: ISupportRepository, user_repository: IUserRepository):
        self.support_repository = support_repository
        self.user_repository = user_repository
    
    def create_support_ticket(self, user_id: int, title: str, issue_description: str = None) -> Support:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Create support ticket
        support = Support(
            SupportID=None,
            UserID=user_id,
            Status='open',
            Create_at=datetime.now(),
            Updated_at=None,
            Issue_des=issue_description,
            Title=title
        )
        
        return self.support_repository.add(support)
    
    def get_support_ticket(self, support_id: int) -> Optional[Support]:
        return self.support_repository.get_by_id(support_id)
    
    def get_user_support_tickets(self, user_id: int) -> List[Support]:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return self.support_repository.get_by_user_id(user_id)
    
    def get_all_support_tickets(self) -> List[Support]:
        """Get all support tickets (admin function)"""
        return self.support_repository.get_all()
    
    def get_support_tickets_by_status(self, status: str) -> List[Support]:
        """Get support tickets by status"""
        valid_statuses = ['open', 'in_progress', 'resolved', 'closed']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        return self.support_repository.get_by_status(status)
    
    def update_support_ticket(self, support_id: int, title: str = None, issue_description: str = None, status: str = None) -> Optional[Support]:
        support = self.support_repository.get_by_id(support_id)
        if not support:
            return None
        
        if title:
            support.Title = title
        if issue_description:
            support.Issue_des = issue_description
        if status:
            valid_statuses = ['open', 'in_progress', 'resolved', 'closed']
            if status not in valid_statuses:
                raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
            support.Status = status
        
        support.Updated_at = datetime.now()
        
        return self.support_repository.update(support)
    
    def update_support_status(self, support_id: int, status: str) -> bool:
        """Update only the status of a support ticket"""
        valid_statuses = ['open', 'in_progress', 'resolved', 'closed']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        support = self.support_repository.get_by_id(support_id)
        if not support:
            return False
        
        return self.support_repository.update_status(support_id, status)
    
    def delete_support_ticket(self, support_id: int) -> bool:
        support = self.support_repository.get_by_id(support_id)
        if not support:
            return False
        
        return self.support_repository.delete(support_id)
    
    def close_support_ticket(self, support_id: int) -> bool:
        """Close a support ticket"""
        return self.update_support_status(support_id, 'closed')
    
    def resolve_support_ticket(self, support_id: int) -> bool:
        """Mark a support ticket as resolved"""
        return self.update_support_status(support_id, 'resolved')
