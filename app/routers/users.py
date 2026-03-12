from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, APIRouter
from app.controllers.auth import get_current_user, token_required
from app.dependencies import get_db
from app import schemas, controllers
from app.schemas.auth import CurrentUserToken

router = APIRouter(
    tags=["Users"]
)

# Rota pública para criar um novo usuário
@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return controllers.create_user(db, user)

# Rota para listar todos os usuários
@router.get("/users/", response_model=list[schemas.User], operation_id="get_users")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = controllers.get_users(db, skip=skip, limit=limit)
    return users


@router.post("/users/normalize-dates/")
def normalize_user_dates(db: Session = Depends(get_db)):
    controllers.normalize_user_dates(db)
    return {"message": "Datas normalizadas com sucesso"}

# Rota para obter um usuário específico por ID
@router.get("/users/{user_id}", response_model=schemas.User, dependencies=[Depends(token_required)])
def read_user(user_id: str, db: Session = Depends(get_db)):
    db_user = controllers.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_user

# Rota para atualizar um usuário
@router.put("/users/{user_id}", response_model=schemas.User, dependencies=[Depends(token_required)])
def update_user(user_id: str, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = controllers.update_user(db=db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_user

# Rota para excluir um usuário
@router.delete("/users/{user_id}", response_model=schemas.User, dependencies=[Depends(token_required)])
def delete_user(user_id: str, db: Session = Depends(get_db)):
    db_user = controllers.delete_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_user