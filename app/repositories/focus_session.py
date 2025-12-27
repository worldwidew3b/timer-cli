from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from app.models.focus_session import FocusSession

class FocusSessionRepository:
    @staticmethod
    def create(session: Session, task_id: int, duration: int = 0) -> FocusSession:
        focus_session = FocusSession(task_id=task_id, duration=duration)
        session.add(focus_session)
        try:
            session.commit()
            session.refresh(focus_session)
            return focus_session
        except IntegrityError:
            session.rollback()
            raise ValueError('Invalid task_id or database constraint violation')

    @staticmethod
    def get(session: Session, id: int) -> FocusSession | None:
        return session.scalar(select(FocusSession).where(FocusSession.id == id))

    @staticmethod
    def update(session: Session, id: int, **kwargs) -> FocusSession:
        focus_session = FocusSessionRepository.get(session, id)
        if not focus_session:
            raise ValueError(f'FocusSession with id {id} not found')

        for key, value in kwargs.items():
            if hasattr(focus_session, key):
                setattr(focus_session, key, value)

        # If duration is explicitly provided in kwargs, use that value
        if 'duration' in kwargs:
            focus_session.duration = kwargs['duration']
        elif 'end_time' in kwargs and focus_session.start_time and focus_session.duration == 0:
            # Only calculate duration from timestamps if it hasn't been set already
            focus_session.duration = int((focus_session.end_time - focus_session.start_time).total_seconds())
            print(focus_session.duration)

        session.commit()
        session.refresh(focus_session)
        return focus_session

    @staticmethod
    def get_by_task_id(session: Session, task_id: int) -> list[FocusSession]:
        return list(session.scalars(select(FocusSession).where(FocusSession.task_id == task_id)))

    @staticmethod
    def get_active_sessions(session: Session) -> list[FocusSession]:
        """Возвращает активные сессии (без end_time)"""
        return list(session.scalars(
            select(FocusSession).where(FocusSession.end_time.is_(None))
        ))

    @staticmethod
    def get_total_duration_for_task(session: Session, task_id: int) -> int:
        """Возвращает общую продолжительность всех сессий для задачи"""
        sessions = FocusSessionRepository.get_by_task_id(session, task_id)
        return sum(session.duration for session in sessions)

    @staticmethod
    def get_stats_by(session: Session, period: str, task_id: int | None):
        from app.utils.period_map import PERIOD_MAP
        try:
            days = PERIOD_MAP[period]
        except KeyError:
            print('Укажите правильный период week/month/year/today')
            return None

        # Calculate the date threshold based on the period
        threshold_date = datetime.now() - timedelta(days=days)

        # Build the query based on whether task_id is provided
        query = select(FocusSession).where(FocusSession.created_at >= threshold_date)
        if task_id:
            query = query.where(FocusSession.task_id == task_id)

        sessions = list(session.scalars(query))

        return sessions