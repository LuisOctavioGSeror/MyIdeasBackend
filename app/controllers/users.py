from typing import List
from sqlalchemy.orm import Session
from datetime import datetime, date
from app import models, schemas
from app.dependencies import pwd_context
from app.controllers.auth import get_password_hash
from fastapi import HTTPException

from app.schemas.auth import CurrentUserToken
from app.utils.enums import StatusEnum


# Função para obter um usuário pelo email
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


# Função para obter todos os usuários
def get_users(db: Session, skip: int = 0, limit: int = 100):

    user_list = db.query(
        models.User.id,
        models.User.email,
        models.User.full_name,
        models.User.status,

        models.User.created_at,
        models.User.updated_at,
    ).offset(skip).limit(limit).all()

    # Convert datetime to date for birth_date to match Pydantic schema
    result = []
    for user in user_list:
        # Convert SQLAlchemy Row to dict
        user_dict = {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'created_at': user.created_at,
            'updated_at': user.updated_at,
            'status': user.status
        }
        result.append(user_dict)

    return result


# Função para obter um usuário por ID
def get_user_by_id(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


# Função para criar um novo usuário
def create_user(db: Session, user: schemas.UserCreate):


    hashed_password = get_password_hash(user.password)


    db_user = models.User(
        email=user.email,
        full_name=user.full_name.upper(),
        password=hashed_password,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# Função para atualizar um usuário
def update_user(db: Session, user_id: str, user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        if user.full_name:
            db_user.full_name = user.full_name
        if user.email:
            db_user.email = user.email
        if user.password:
            db_user.hashed_password = pwd_context.hash(user.password)
        if user.status:
            db_user.status = user.status

        db_user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_user)
    return db_user


# Função para excluir um usuário
def delete_user(db: Session, user_id: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user



def normalize_user_dates(db: Session):
    users = db.query(models.User).all()

    for user in users:
        if user.birth_date:
            user.birth_date = datetime.now().date()
        if user.created_at:
            user.created_at = datetime.now().date()
        if user.updated_at:
            user.updated_at = datetime.now().date()

    db.commit()
    return users