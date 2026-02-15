from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role:Optional[str]="user"

class UserOut(UserBase):
    id: int
    role:str
    status:str

    model_config=ConfigDict(from_attributes=True)
    @field_validator("role", mode="before")
    @classmethod
    def get_role_name(cls, value):
        if hasattr(value, "name"):
            return value.name
        return value

class UserLogin(UserBase):
    password: str

class AdminStats(BaseModel):
    total_users:int
    users_by_status: dict[str, int]
    total_tasks: int
    tasks_by_status: dict[str, int]