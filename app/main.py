from fastapi import FastAPI
from app.routers import tasks, users
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application starting...")
    yield 
    print("Shut down...")

app = FastAPI(lifespan=lifespan)

app.include_router(tasks.router, tags=["Tasks"])
app.include_router(users.router, tags=["Users"])

@app.get("/")
def root():
    return {"message": "Welcome to Task Master API"}