from datetime import datetime
from .base import Base
from sqlalchemy.orm import mapped_column, Mapped

class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    time_spent: Mapped[int] = mapped_column(default=0)
    