from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.task import TaskCreate
from app.database import get_db
from app.utils.security import get_current_user, admin_required
from sqlalchemy.orm import Session, joinedload
from app.models.database_models import Task, User, UserStatus, TaskStatus
from app.models.task import TaskOut, TaskUpdate

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
    query = db.query(Task).options(joinedload(Task.owner))
    if search:
        query=query.filter(Task.title.ilike(f"%{search}%"))
    
    if status:
        query = query.filter(Task.status == status)
    
    if user_id:
        query = query.filter(Task.owner_id == user_id)

    tasks=query.offset(skip).limit(limit).all()
    return tasks



@router.get("/my-tasks", response_model=list[TaskOut])
async def get_my_tasks(limit:int=Query(default=10, ge=1, le=100), skip:int=Query(default=0, ge=0), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks=db.query(Task).filter(Task.owner_id==current_user.id).offset(skip).limit(limit).all()
    return tasks

@router.get("/tasks/{id}", response_model=TaskOut)
async def get_task(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/tasks")
async def create_task(task_data: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_task=Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        due_date=task_data.due_date,
        owner_id=current_user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.delete("/tasks/{id}", status_code=204)
async def delete_task(id: int, db:Session=Depends(get_db), user:User=Depends(get_current_user)):  
    task=db.query(Task).filter(Task.id==id).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if not task.owner_id==user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to delete this task.")
    
    db.delete(task)
    db.commit()
    return

@router.patch("/tasks/{id}", response_model=TaskOut)
async def update_task(id: int, task_update: TaskUpdate, db: Session=Depends(get_db), current_user:User=Depends(get_current_user)):
    task=db.query(Task).filter(Task.id==id).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    is_owner = task.owner_id == current_user.id
    is_active_admin = (current_user.role.name == "admin" and current_user.status == UserStatus.ACTIVE)
    if not is_owner and not is_active_admin:
        raise HTTPException(status_code=403, detail="You are not allowed to update this task.")
    
    update_data=task_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task
