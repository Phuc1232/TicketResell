from datetime import datetime
from typing import Optional

class User:
    def __init__(self, id: Optional[int], phone_number: str, username: str, status: str,
                 password_hash: str, email: str, date_of_birth, create_date, role_id: int,
                 verified: bool = False, verification_code: Optional[str] = None,
                 verification_expires_at: Optional[datetime] = None):
        self.id = id
        self.phone_number = phone_number
        self.username = username
        self.status = status
        self.password_hash = password_hash
        self.email = email
        self.date_of_birth = date_of_birth
        self.create_date = create_date
        self.role_id = role_id
        self.verified = verified
        self.verification_code = verification_code
        self.verification_expires_at = verification_expires_at