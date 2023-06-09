from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


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


@app.post(
    "/login/",
)
def login(email: str, password: str, db: Session = Depends(get_db)):
    db_user = crud.validate_credentials(db, email=email, password=password)
    if db_user is None:
        return {"Details": "Please enter valid credentials"}
    return {"Details": "User logged in successfully"}
