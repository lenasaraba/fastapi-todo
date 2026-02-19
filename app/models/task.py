# app/models/task.py
from pydantic import BaseModel, computed_field, field_validator, EmailStr
from datetime import datetime, timezone
from typing import Optional
from .database_models import TaskStatus, TaskCategory
from .user import UserOut

class TaskBase(BaseModel): 
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class DateValidationMixIn:
    @field_validator('due_date')
    @classmethod
    def date_must_be_in_future(cls, input_date:datetime):
        if input_date.tzinfo is None:
            input_date = input_date.replace(tzinfo=timezone.utc)
        if input_date and input_date<datetime.now(timezone.utc):
            raise ValueError("Due date cannot be a past time.")
        return input_date

class Task(TaskBase):
    id: Optional[int] = None
    status: str=TaskStatus.TODO

class TaskCreate(BaseModel, DateValidationMixIn):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str=TaskStatus.TODO
    category: TaskCategory = TaskCategory.OTHER

class UserSummary(BaseModel):
    full_name: Optional[str]
    email: EmailStr
    class Config:
        from_attributes = True

class TaskOut(TaskBase):
    id: int
    owner_id: int
    owner: UserSummary
    status: TaskStatus
    category: TaskCategory

    @computed_field
    @property
    def status_display(self) -> str:
        mapping = {
            TaskStatus.TODO: "To Do",
            TaskStatus.IN_PROGRESS: "In Progress",
            TaskStatus.DONE: "Done"
        }
        return mapping.get(self.status, "Unknown")

    class Config:
        from_attributes = True

class TaskUpdate(BaseModel, DateValidationMixIn):
    title: Optional[str]=None
    description: Optional[str]=None
    status: Optional[TaskStatus]=None
    due_date: Optional[datetime]=None
    category: Optional[TaskCategory]=None