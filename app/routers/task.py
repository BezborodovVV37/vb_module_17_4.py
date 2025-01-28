from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import Task, User
from app.schemas import CreateTask, UpdateTask
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(prefix='/task', tags=['task'])


@router.get('/')
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task)).all()
    return tasks


@router.get('/task_id')
async def task_by_id(task_id: int,
                     db: Annotated[Session, Depends(get_db)]):
    task = db.scalars(select(Task).where(Task.id == task_id)).first()

    if task:
        return task

    else:
        raise HTTPException(status_code=404, detail="Task was not found")


@router.post('/create')
async def create_task(user_id: int,
                      db: Annotated[Session, Depends(get_db)],
                      create_task: CreateTask):
    user = db.scalars(select(User).where(User.id == user_id))

    if user:
        db.execute(insert(Task).values(
            title=create_task.title,
            content=create_task.content,
            priority=create_task.priority,
            user_id=user_id,
            slug=slugify(create_task.title)
        ))
        db.commit()
        return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}

    else:
        raise HTTPException(status_code=404, detail="User was not found")


@router.put('/update')
async def update_task(task_id: int,
                      db: Annotated[Session, Depends(get_db)],
                      update_task: UpdateTask):
    task = db.scalar(select(Task).where(Task.id == task_id))

    if task is not None:
        db.execute(update(Task).where(Task.id == task_id).values(
            title=update_task.title,
            content=update_task.content,
            priority=update_task.priority
        ))
        db.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'Task update is successful!'}

    raise HTTPException(status_code=404, detail="Task was not found")


@router.delete('/delete')
async def delete_task(task_id: int,
                      db: Annotated[Session, Depends(get_db)]):
    task = db.scalar(select(Task).where(Task.id == task_id))

    if task:
        db.execute(delete(Task).where(Task.id == task_id))
        db.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'Task deleted successfully!'}

    else:
        raise HTTPException(status_code=404, detail="Task was not found")