from fastapi import APIRouter, Depends, Query
from app.models.task import TaskCreate
from app.database import get_db
from app.utils.security import get_current_user, admin_required
from sqlalchemy.orm import Session, joinedload
from app.models.database_models import User, TaskStatus
from app.models.task import TaskOut, TaskUpdate
from app.services.task_service import TaskService

router=APIRouter()

@router.get("/tasks", response_model=list[TaskOut])
async def get_all_tasks(
    search: str = Query(None, min_length=3),
    status: TaskStatus = Query(None),       
    user_id: int = Query(None), 
    limit: int = Query(default=10, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
    db: Session = Depends(get_db), 
    admin:User=Depends(admin_required)
):
    return TaskService.get_all_tasks(db, search, status, user_id, limit, skip)
    
@router.get("/my-tasks", response_model=list[TaskOut])
async def get_my_tasks(limit:int=Query(default=10, ge=1, le=100), skip:int=Query(default=0, ge=0), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return TaskService.get_user_tasks(db, current_user, limit, skip)

@router.get("/tasks/{id}", response_model=TaskOut)
async def get_task(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return TaskService.get_task(id, db, current_user)

@router.post("/tasks")
async def create_task(task_data: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return TaskService.create_task(task_data, db, current_user)

@router.delete("/tasks/{id}", status_code=204)
async def delete_task(id: int, db:Session=Depends(get_db), user:User=Depends(get_current_user)):  
    TaskService.delete_task(db, id, user)
    return

@router.patch("/tasks/{id}", response_model=TaskOut)
async def update_task(id: int, task_update: TaskUpdate, db: Session=Depends(get_db), current_user:User=Depends(get_current_user)):
    return TaskService.update_task(db, current_user, id, task_update)
