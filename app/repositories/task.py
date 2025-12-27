from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.task import Task
class TaskRepository:
    @staticmethod
    def create(session: Session, name: str) -> Task:
        task = Task(name=name)
        session.add(task)
        try: 
            session.commit()
            session.refresh(task)
            return task
        except IntegrityError:
            session.rollback()
        
    @staticmethod
    def get(session: Session, id: int):
        task = session.scalar(select(Task).where(Task.id == id))
        if task:
            return task
        
    @staticmethod
    def update(session: Session, id: int, time: int):
        task = TaskRepository.get(session, id)
        if not task:
            return
        task.time_spent += time
        session.commit()
        session.refresh(task)
        return task
    
    @staticmethod
    def delete(session: Session, id: int):
        task = TaskRepository.get(session, id)
        if not task:
            return False
        session.delete(task)
        session.commit()
        return True
    
    @staticmethod
    def get_all(session: Session) -> list[Task]:
        return list(session.scalars(select(Task)))