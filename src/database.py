"""
Database configuration and models for activity management system
"""

from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from pathlib import Path

# Create database directory if it doesn't exist
db_dir = Path(__file__).parent / "data"
db_dir.mkdir(exist_ok=True)

# Database URL - using SQLite for simplicity
DATABASE_URL = f"sqlite:///{db_dir}/activities.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


# Association table for many-to-many relationship between activities and participants
activity_participants = Table(
    'activity_participants',
    Base.metadata,
    Column('activity_id', Integer, ForeignKey('activity.id'), primary_key=True),
    Column('participant_email', String, ForeignKey('participant.email'), primary_key=True)
)


class Activity(Base):
    """Activity model for database"""
    __tablename__ = "activity"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    schedule = Column(String)
    max_participants = Column(Integer)
    participants = relationship(
        "Participant",
        secondary=activity_participants,
        back_populates="activities"
    )

    def to_dict(self):
        """Convert to dictionary format matching original API"""
        return {
            "id": self.id,
            "description": self.description,
            "schedule": self.schedule,
            "max_participants": self.max_participants,
            "participants": [p.email for p in self.participants]
        }


class Participant(Base):
    """Participant/email model for database"""
    __tablename__ = "participant"

    email = Column(String, primary_key=True, index=True)
    activities = relationship(
        "Activity",
        secondary=activity_participants,
        back_populates="participants"
    )


# Create all tables
Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
