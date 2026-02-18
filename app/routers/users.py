from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import UserCreate, UserOut, AdminStats
from app.database import get_db
from app.utils.security import hash_password, verify_password, create_access_token, admin_required, check_if_admin_exists
from fastapi.security import OAuth2PasswordRequestForm
from app.models.database_models import User, Role, UserStatus, Task
from sqlalchemy.orm import Session
from app.database import get_db
from sqlalchemy import func
from app.services.user_service import UserService

router = APIRouter()

@router.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    return UserService.register(db, user)

@router.post("/login")
async def login(login_data: OAuth2PasswordRequestForm=Depends(), db: Session = Depends(get_db)):
    return UserService.login(db, login_data.username, login_data.password)

@router.get("/admin/users")
async def get_all_users(db: Session=Depends(get_db), admin: User=Depends(admin_required)):
    return UserService.get_all_users(db)

@router.get("/pending-users", response_model=list[UserOut])
async def get_pending_users(db: Session=Depends(get_db), admin: User=Depends(admin_required)):
    return UserService.get_pending_users(db)

@router.patch("/users/{user_id}/process-approval")
async def process_user_approval(user_id:int, approve: bool,db: Session=Depends(get_db), admin: User=Depends(admin_required)):
    return UserService.process_user(db, user_id, approve)

@router.get("/admin/stats", response_model=AdminStats)
async def get_admin_stats(db: Session=Depends(get_db), admin: User=Depends(admin_required)):
    return UserService.get_admin_data(db)

@router.delete("/admin/users/{user_id}", status_code=status.HTTP_200_OK)
async def arhive_user(user_id:int, db:Session=Depends(get_db), admin:User=Depends(admin_required)):
    user= UserService.archive_user(db, user_id, admin)
    return {"message": f"User {user.email} archived."}
