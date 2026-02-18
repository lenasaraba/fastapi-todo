from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, status
from app.models.database_models import User, Role, UserStatus
from app.database import get_db
from app.core.config import settings

load_dotenv()

SECRET_KEY =settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password:str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password:str, hashed_password:str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data:dict, expires_delta: Optional[timedelta] = None):
    to_encode=data.copy()
    if expires_delta:
        expire=datetime.now(timezone.utc) + expires_delta
    else:
        expire=datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt=jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token:str):
    try:
        payload=jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None 
        return email
    except Exception:
        return None
    
async def get_current_user(token: str=Depends(oauth2_scheme), db: Session=Depends(get_db)) -> User:
    email=verify_access_token(token)
    if email is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user=db.query(User).filter(User.email==email).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

def admin_required(current_user: User=Depends(get_current_user)):
    if current_user.role.name !="admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized for this action. Required role: ADMIN."
        )
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is waiting for an approval."
        )
    
    return current_user

def check_if_admin_exists(db: Session)->bool:
    return db.query(User).join(Role).filter(Role.name == "admin").first() is not None