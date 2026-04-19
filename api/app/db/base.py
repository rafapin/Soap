from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


# Import all models so they register with Alembic
from app.db.models.alarm import Alarm
from app.db.models.ingestion_batch import IngestionBatch
from app.db.models.alarm_rejection import AlarmRejection
