from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, APIRouter
from app.controllers.auth import token_required, get_current_user
from app.dependencies import get_db
from app import schemas, controllers
from app.schemas.auth import CurrentUserToken

router = APIRouter(tags=["Ideas"])


@router.post("/ideas/", response_model=schemas.Idea, dependencies=[Depends(token_required)])
def create_idea(
    idea: schemas.IdeaCreate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    user_id = current["user_id"]
    return controllers.create_idea(db, idea, user_id)


@router.get("/ideas/", response_model=list[schemas.Idea], dependencies=[Depends(token_required)])
def read_ideas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current: CurrentUserToken = Depends(get_current_user),
):
    return controllers.get_ideas_by_user(db, user_id=current["user_id"], skip=skip, limit=limit)


@router.get("/users/{user_id}/ideas/", response_model=list[schemas.Idea], dependencies=[Depends(token_required)])
def read_user_ideas(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current: CurrentUserToken = Depends(get_current_user),
):
    if user_id != current["user_id"]:
        raise HTTPException(status_code=403, detail="Not allowed to list another user's ideas")
    return controllers.get_ideas_by_user(db, user_id=current["user_id"], skip=skip, limit=limit)


@router.get("/ideas/{idea_id}", response_model=schemas.Idea, dependencies=[Depends(token_required)])
def read_idea(
    idea_id: str,
    db: Session = Depends(get_db),
    current: CurrentUserToken = Depends(get_current_user),
):
    db_idea = controllers.get_idea_by_id(db, idea_id=idea_id, user_id=current["user_id"])
    if db_idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    return db_idea


@router.put("/ideas/{idea_id}", response_model=schemas.Idea, dependencies=[Depends(token_required)])
def update_idea(
    idea_id: str,
    idea: schemas.IdeaUpdate,
    db: Session = Depends(get_db),
    current: CurrentUserToken = Depends(get_current_user),
):
    db_idea = controllers.update_idea(db=db, idea_id=idea_id, idea=idea, user_id=current["user_id"])
    if db_idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    return db_idea


@router.delete("/ideas/{idea_id}", response_model=schemas.Idea, dependencies=[Depends(token_required)])
def delete_idea(
    idea_id: str,
    db: Session = Depends(get_db),
    current: CurrentUserToken = Depends(get_current_user),
):
    db_idea = controllers.delete_idea(db=db, idea_id=idea_id, user_id=current["user_id"])
    if db_idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    return db_idea

