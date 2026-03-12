from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from app.schemas.users import User
from app.utils import enums
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas, dependencies
from app.controllers.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
)

router = APIRouter(tags=["Auth"])


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    company_id: Optional[str] = Query(
        None, description="Optional company ID to login to a specific company"
    ),
    db: Session = Depends(dependencies.get_db),
) -> schemas.AuthLoginResponse:
    # Obs: form_data.username represents the user email.
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=float(dependencies.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
        },
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.post("/auth/login", response_model=schemas.AuthLoginResponse)
async def login_json(
    credentials: schemas.UserLogin,
    db: Session = Depends(dependencies.get_db),
) -> schemas.AuthLoginResponse:
    user = authenticate_user(db, credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=float(dependencies.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
        },
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.post("/auth/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(dependencies.get_db),
) -> schemas.User:
    existing_user = (
        db.query(models.User).filter(models.User.email == user_in.email).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já cadastrado",
        )

    hashed_password = get_password_hash(user_in.password)
    db_user = models.User(
        email=user_in.email,
        full_name=user_in.full_name,
        password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/auth/me", response_model=schemas.User)
def read_current_user(
    current=Depends(get_current_user),
    db: Session = Depends(dependencies.get_db),
) -> schemas.User:
    user_id = current["user_id"]
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    return user