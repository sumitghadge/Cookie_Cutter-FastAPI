from sqlalchemy.orm import Session

from . import models


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def validate_credentials(db: Session, email: str, password: str):
    return (
        db.query(models.User)
        .filter(models.User.email == email, models.User.hashed_password == password)
        .first()
    )


def create_user(db: Session, user: dict):
    fake_hashed_password = user["password"]
    db_user = models.User(
        name=user["name"], email=user["email"], hashed_password=fake_hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
