from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import User, Task
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router.get("/user_id'")
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user_id = db.scalars(select(User).where(User.id == user_id))
    if user_id is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )
    return user_id


@router.post("/create")
async def create_user(create: CreateUser, db: Annotated[Session, Depends(get_db)]):
    db.execute(insert(User).values(
        username=create.username,
        firstname=create.firstname,
        lastname=create.lastname,
        age=create.age,
        slug=slugify(create.username)))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router.put('/update')
async def update_user(db: Annotated[Session, Depends(get_db)], user_id: int,
                      update_user: UpdateUser):
    user = db.scalars(select(User).where(User.id == user_id)).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    db.execute(update(User).where(User.id == user_id).values(
        firstname=update_user.firstname,
        lastname=update_user.lastname,
        age=update_user.age
    ))
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}


@router.delete("/delete")
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user_delete = db.scalars(select(User).where(User.id == user_id)).first()
    if user_delete is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )
    else:
        db.execute(delete(User).where(User.id == user_id))
        db.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}


@router.get("/user_id/tasks")
async def tasks_by_user_id(user_id: int,
                           db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task).where(Task.user_id == user_id)).all()
    return tasks