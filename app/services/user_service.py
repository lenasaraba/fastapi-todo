from sqlalchemy.orm import Session
from app.models.user import UserCreate
from app.models.database_models import User, Role, UserStatus, Task, TaskStatus
from fastapi import HTTPException, status
from sqlalchemy import func
from app.utils.security import check_if_admin_exists, hash_password, create_access_token, verify_password

class UserService:
    @staticmethod
    def register(db: Session, user: UserCreate)-> User:
        existing_user=db.query(User).filter(User.email==user.email).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
        requested_role=(user.role or "user").lower()
        role=db.query(Role).filter(func.lower(Role.name)==requested_role).first()

        if role is None:
            raise HTTPException(status_code=500, detail="Role not found.")
        
        user_status=UserStatus.ACTIVE

        if role.name=="admin":
            if check_if_admin_exists(db):
                user_status=UserStatus.PENDING

        hashed=hash_password(user.password)
        new_user=User(
            email=user.email,
            hashed_password=hashed,
            full_name=user.full_name,
            role_id=role.id,
            status=user_status.value
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def login(db: Session, email: str, password:str)-> dict:
        user=db.query(User).filter(User.email==email).first()

        if user is None or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        if user.status==UserStatus.ARCHIVED.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account has been archived and is no longer active.")
        
        if user.status==UserStatus.PENDING.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your account is still waiting for an approval. Please be patient.")
        access_token_data={"sub": user.email, "role":user.role.name}
        access_token=create_access_token(data=access_token_data)
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def get_all_users(db:Session)-> list[User]:
        return db.query(User).all()
    
    @staticmethod
    def get_pending_users(db: Session)->list[User]:
        return db.query(User).filter(User.status==UserStatus.PENDING.value).all()
    
    @staticmethod
    def process_user(db: Session, user_id: int, approve: bool)-> User:
        target_user=db.query(User).filter(User.id==user_id).first()

        if target_user is None:
            raise HTTPException(status_code=404, detail="User for approval does not exist.")
        if target_user.status == UserStatus.ACTIVE.value:
            raise HTTPException(status_code=400, detail="User is already active.")
        if not approve:
            user_role=db.query(Role).filter(func.lower(Role.name)=="user").first()
            if user_role is None:
                raise HTTPException(status_code=500, detail="You cannot switch an user to a role that does not exist")
            target_user.role_id=user_role.id

        target_user.status=UserStatus.ACTIVE.value

        db.commit()
        db.refresh(target_user)
        return target_user
    
    @staticmethod
    def get_admin_data(db: Session)->dict:
        total_users=db.query(User).count()
        user_stats_raw=db.query(User.status, func.count(User.id)).group_by(User.status).all()
        users_by_status={status.value: count for status, count in user_stats_raw}

        total_tasks=db.query(Task).count()
        task_stats_raw=db.query(Task.status, func.count(Task.id)).group_by(Task.status).all()
        tasks_by_status={status.value: count for status, count in task_stats_raw}

        return {
            "total_users": total_users,
            "users_by_status": users_by_status,
            "total_tasks": total_tasks,
            "tasks_by_status": tasks_by_status
        }  
    
    @staticmethod
    def archive_user(db: Session, user_id: int, admin:User)->User:
        if user_id == admin.id:
            raise HTTPException(status_code=400, detail="You cannot archive your own account.")
    
        target_user=db.query(User).filter(User.id==user_id).first()

        if target_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        target_user.status=UserStatus.ARCHIVED.value
        db.commit()
        db.refresh(target_user)
        return target_user
        