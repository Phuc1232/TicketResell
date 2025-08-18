from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.user_model import UserModel
from domain.models.user import User
from domain.models.iuser_repository import IUserRepository


class UserRepository(IUserRepository):
    def __init__(self, session: Session = session):
        self.session = session

    # ORM -> Domain
    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=model.UserId,
            phone_number=model.Phone_Number,
            username=model.UserName,
            status=model.Status,
            password_hash=model.Password,
            email=model.Email,
            date_of_birth=model.Date_Of_Birth,
            create_date=model.Create_Date,
            role_id=model.RoleID,
            verified=model.verified,
            verification_code=model.verification_code,
            verification_expires_at=model.verification_expires_at
        )

    # Domain -> ORM
    def _to_orm(self, user: User) -> UserModel:
        return UserModel(
            UserId=user.id,
            Phone_Number=user.phone_number,
            UserName=user.username,
            Status=user.status,
            Password=user.password_hash,
            Email=user.email,
            Date_Of_Birth=user.date_of_birth,
            Create_Date=user.create_date,
            RoleID=user.role_id,
            verified=user.verified,
            verification_code=user.verification_code,
            verification_expires_at=user.verification_expires_at
        )

    def add(self, user: User) -> User:
        try:
            model = self._to_orm(user)
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return self._to_domain(model)
        except Exception:
            self.session.rollback()
            raise
        finally:
            self.session.close()

    def get_by_email(self, email: str) -> Optional[User]:
        model = self.session.query(UserModel).filter_by(Email=email).first()
        return self._to_domain(model) if model else None

    def get_by_id(self, user_id: int) -> Optional[User]:
        model = self.session.query(UserModel).filter_by(UserId=user_id).first()
        return self._to_domain(model) if model else None

    def list(self) -> List[User]:
        models = self.session.query(UserModel).all()
        return [self._to_domain(m) for m in models]

    def update(self, user: User) -> User:
        try:
            model = self.session.query(UserModel).filter_by(UserId=user.id).first()
            if not model:
                raise ValueError("User not found")

            model.Phone_Number = user.phone_number
            model.UserName = user.username
            model.Status = user.status
            model.Email = user.email
            model.Date_Of_Birth = user.date_of_birth
            model.RoleID = user.role_id
            # Update verification fields
            model.verified = user.verified
            model.verification_code = user.verification_code
            model.verification_expires_at = user.verification_expires_at

            self.session.commit()
            self.session.refresh(model)
            return self._to_domain(model)
        except Exception:
            self.session.rollback()
            raise
        finally:
            self.session.close()

    def delete(self, user_id: int) -> None:
        try:
            model = self.session.query(UserModel).filter_by(UserId=user_id).first()
            if model:
                self.session.delete(model)
                self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        finally:
            self.session.close()
