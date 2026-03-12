from sqlalchemy.orm import Session
from datetime import datetime
from app import models, schemas
from fastapi import HTTPException


def get_ideas(db: Session, skip: int = 0, limit: int = 100):
    idea_list = (
        db.query(
            models.Idea.id,
            models.Idea.title,
            models.Idea.description,
            models.Idea.status,
            models.Idea.image_url,
            models.Idea.user_id,
            models.Idea.created_at,
            models.Idea.updated_at,
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for idea in idea_list:
        result.append(
            {
                "id": idea.id,
                "title": idea.title,
                "description": idea.description,
                "status": idea.status,
                "image_url": idea.image_url,
                "user_id": idea.user_id,
                "created_at": idea.created_at,
                "updated_at": idea.updated_at,
            }
        )

    return result


def get_ideas_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    idea_list = (
        db.query(models.Idea)
        .filter(models.Idea.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return idea_list


def get_idea_by_id(db: Session, idea_id: str, user_id: str | None = None):
    q = db.query(models.Idea).filter(models.Idea.id == idea_id)
    if user_id is not None:
        q = q.filter(models.Idea.user_id == user_id)
    return q.first()


def create_idea(db: Session, idea: schemas.IdeaCreate, user_id: str):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    db_idea = models.Idea(
        title=idea.title,
        description=idea.description,
        status=idea.status,
        image_url=idea.image_url,
        user_id=user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    return db_idea


def update_idea(db: Session, idea_id: str, idea: schemas.IdeaUpdate, user_id: str | None = None):
    db_idea = db.query(models.Idea).filter(models.Idea.id == idea_id).first()
    if not db_idea:
        return None
    if user_id is not None and db_idea.user_id != user_id:
        return None

    if idea.title is not None:
        db_idea.title = idea.title
    if idea.description is not None:
        db_idea.description = idea.description
    if idea.status is not None:
        db_idea.status = idea.status
    if idea.image_url is not None:
        db_idea.image_url = idea.image_url

    db_idea.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_idea)
    return db_idea


def delete_idea(db: Session, idea_id: str, user_id: str | None = None):
    db_idea = db.query(models.Idea).filter(models.Idea.id == idea_id).first()
    if not db_idea:
        return None
    if user_id is not None and db_idea.user_id != user_id:
        return None

    db.delete(db_idea)
    db.commit()
    return db_idea

