from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.task import Task
from app.models.focus_session import FocusSession
import os

# Get the directory where this script is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Build path to the database file in the project root
db_path = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'focus_tracker.db')
# Create database engine with the relative path
engine = create_engine(f'sqlite:///{db_path}')
# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database and create tables"""
    Base.metadata.create_all(bind=engine)
