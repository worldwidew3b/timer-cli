from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.task import Task
from app.models.focus_session import FocusSession

# Create database engine
engine = create_engine('sqlite:///focus_tracker.db')

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database and create tables"""
    Base.metadata.create_all(bind=engine)
