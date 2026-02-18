from app.models.database_models import TaskStatus, Task, User, UserStatus
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from app.models.task import TaskCreate, TaskUpdate

class TaskService:
    @staticmethod
    def get_all_tasks(db: Session, 
        search: str = None, 
        status: TaskStatus = None, 
        user_id: int = None, 
        limit: int = 10, 
        skip: int = 0
    ):
        query=db.query(Task).options(joinedload(Task.owner))

        if search:
            query=query.filter(Task.title.ilike(f"%{search}%"))

        if status:
            query=query.filter(Task.status==status)

        if user_id:
            query=query.filter(Task.owner_id==user_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_tasks(db: Session, user: User, limit: int, skip: int) -> list[Task]:
        return db.query(Task).filter(Task.owner_id==user.id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_task(id: int, db: Session, user: User):
        task= db.query(Task).filter(Task.owner_id==user.id, Task.id==id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task      
    
    @staticmethod
    def create_task(task_data: TaskCreate, db: Session, current_user: User)->Task:
        new_task=Task(**task_data.model_dump(), owner_id=current_user.id)
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
    
    @staticmethod
    def delete_task(db: Session, id: int, user:User)->None:
        task=db.query(Task).filter(Task.id==id).first()

        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        role_name = getattr(user.role, "name", None)
        if task.owner_id!=user.id and (role_name!="admin" or user.status!=UserStatus.ACTIVE):
            raise HTTPException(status_code=403, detail="You are not allowed to delete this task.")
        db.delete(task)
        db.commit()
        return
    
    @staticmethod
    def update_task(db: Session, user: User, id: int, task_update: TaskUpdate)-> Task:
        task= db.query(Task).filter(Task.id==id).first()

        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        is_owner=task.owner_id==user.id
        role_name = getattr(user.role, "name", None)
        is_active_admin=role_name=="admin" and user.status==UserStatus.ACTIVE

        if not is_owner and not is_active_admin:
            raise HTTPException(status_code=403, detail="You are not allowed to update this task.")
        
        update_data=task_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)

        db.commit()
        db.refresh(task)
        return task
        
