import os

from celery import Celery
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


load_dotenv(".env")

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND")


@celery.task(name="create_task", serializer="json")
def create_task(user_dict: dict, db_url):
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        db_user = crud.get_user_by_email(db, email=user_dict["email"])
        if db_user:
            db.close()
            return None
        user = crud.create_user(db=db, user=user_dict)
        new_user = {
            key: value
            for key, value in user.__dict__.items()
            if not key.startswith("_")
        }
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()
    return new_user


@celery.task(name="login_task", serializer="json")
def login_task(email: str, password: str, db_url):
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        db_user = crud.validate_credentials(db=db, email=email, password=password)
        if db_user is None:
            msg = {"Details": "Please enter valid credentials"}
        else:
            msg = {"Details": "User logged in successfully"}
    except:
        db.rollback()
        raise
    finally:
        db.close()
    return msg


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/signup/", response_model=schemas.User)
def sign_up(user: schemas.UserCreate, db: Session = Depends(get_db)):
    data = create_task.delay(user.dict(), str(db.bind.url))
    if not data.get():
        raise HTTPException(status_code=400, detail="Email already registered")
    return data.get()


@app.post("/login/")
def login(email: str, password: str, db: Session = Depends(get_db)):
    data = login_task.delay(email, password, str(db.bind.url))
    return data.get()
