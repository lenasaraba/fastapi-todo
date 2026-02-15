import enum
from sqlalchemy import Integer, Column, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship 
from app.database import Base
from sqlalchemy.sql import func

class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class UserStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

class User(Base):
    __tablename__="users"

    id=Column(Integer, primary_key=True, index=True)
    email=Column(String, unique=True, index=True)
    hashed_password=Column(String)
    full_name=Column(String, nullable=True)
    role_id=Column(Integer, ForeignKey("roles.id"))
    status=Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)

    role=relationship("Role", back_populates="users")
    tasks = relationship("Task", back_populates="owner")

class Task(Base):
    __tablename__="tasks"

    id=Column(Integer, primary_key=True, index=True)
    title=Column(String, nullable=False)
    description=Column(String, nullable=True)
    status=Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    due_date=Column(DateTime, nullable=True)

    created_at=Column(DateTime(timezone=True), server_default=func.now())

    owner_id=Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="tasks")

class Role(Base):
    __tablename__="roles"

    id=Column(Integer, primary_key=True, index=True)
    name=Column(String, unique=False, index=True)

    users=relationship("User", back_populates="role")