from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import UserCreate, UserOut, AdminStats
from app.database import get_db
from app.utils.security import hash_password, verify_password, create_access_token, admin_required, check_if_admin_exists
from fastapi.security import OAuth2PasswordRequestForm
from app.models.database_models import User, Role, UserStatus, Task
from sqlalchemy.orm import Session
from app.database import get_db
from sqlalchemy import func

router = APIRouter()

@router.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    requested_role = (user.role or "user").lower()
    role=db.query(Role).filter(func.lower(Role.name)==requested_role).first()
    if not role:
        raise HTTPException(status_code=500, detail="Role not found.")
    
    user_status=UserStatus.ACTIVE
    
    if role.name=="admin":
        if check_if_admin_exists(db):
            user_status=UserStatus.PENDING

    hashed=hash_password(user.password)
    new_user = User(
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

@router.post("/login")
async def login(login_data: OAuth2PasswordRequestForm=Depends(), db: Session = Depends(get_db)):
    user=db.query(User).filter(User.email==login_data.username).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.status == UserStatus.ARCHIVED.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been archived and is no longer active."
        )
    if user.status == UserStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is still waiting for an approval. Please be patient."
        )
    access_token_data = {"sub": user.email, "role":user.role.name}
    access_token = create_access_token(data=access_token_data)
    return {
            "access_token": access_token, 
            "token_type": "bearer"
        }

@router.get("/admin/users")
async def get_all_users(db: Session=Depends(get_db), admin: User=Depends(admin_required)):
    return db.query(User).all()

@router.get("/pending-users", response_model=list[UserOut])
async def get_pending_users(db: Session=Depends(get_db), admin: User=Depends(admin_required)):
    return db.query(User).filter(User.status==UserStatus.PENDING).all()

@router.patch("/users/{user_id}/process-approval")
async def process_user_approval(user_id:int, approve: bool,db: Session=Depends(get_db), admin: User=Depends(admin_required)):
    target_user=db.query(User).filter(User.id==user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User for approval not found")
    
    if not approve:
        user_role=db.query(Role).filter(func.lower(Role.name)=='user').first()
        if not user_role:
            raise HTTPException(status_code=500, detail="Role 'User' does not exist.")
        target_user.role_id=user_role.id
    
    target_user.status=UserStatus.ACTIVE

    db.commit()
    db.refresh(target_user)
    return target_user

@router.get("/admin/stats", response_model=AdminStats)
async def get_admin_stats(db: Session=Depends(get_db), admin: User=Depends(admin_required)):
    total_users=db.query(User).count()
    user_stats_row=db.query(User.status, func.count(User.id)).group_by(User.status).all()
    users_by_status={status.value: count for status, count in user_stats_row}

    total_tasks = db.query(Task).count()
    task_stats_raw = db.query(Task.status, func.count(Task.id)).group_by(Task.status).all() 
    tasks_by_status = {status.value: count for status, count in task_stats_raw}

    return {
        "total_users": total_users,
        "users_by_status": users_by_status,
        "total_tasks": total_tasks,
        "tasks_by_status": tasks_by_status
    }  

@router.delete("/admin/users/{user_id}", status_code=status.HTTP_200_OK)
async def arhive_user(user_id:int, db:Session=Depends(get_db), admin:User=Depends(admin_required)):
    target_user = db.query(User).filter(User.id == user_id).first()
    if target_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if target_user.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot archive your own account.")
    target_user.status = UserStatus.ARCHIVED
    db.commit()
    db.refresh(target_user)
    
    return {"message": f"User {target_user.email} has been successfully archived."}
