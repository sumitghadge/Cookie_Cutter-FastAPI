import os

from celery import Celery
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


load_dotenv(".env")

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND")


@celery.task(name="create_task")
def create_task():
    return "This task is from celery"


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/signup/", response_model=schemas.User)
def sign_up(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/login/")
def login(email: str, password: str, db: Session = Depends(get_db)):
    db_user = crud.validate_credentials(db, email=email, password=password)
    if db_user is None:
        return {"Details": "Please enter valid credentials"}
    return {"Details": "User logged in successfully"}
