from fastapi import FastAPI
from app.routers import tasks, users
from app.database import engine, SessionLocal
from app.models import database_models
from app.utils.seed import seed_roles
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    database_models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_roles(db)  
    finally:
        db.close()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(tasks.router, tags=["Tasks"])
app.include_router(users.router, tags=["Users"])

@app.get("/")
def root():
    return {"message": "Welcome to Task Master API"}