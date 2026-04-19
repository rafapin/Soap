from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_db
from app.db.base import Base
from app.main import app

# Create in-memory SQLite database for test purposes
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def setup_database() -> Generator[None, None, None]:
    """Create the test database tables once for the whole session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_database: None) -> Generator[Session, None, None]:
    """Yield a new testing session for each test to keep isolation mostly intact."""
    session = TestingSessionLocal()
    try:
        # Note: SQLite in-memory isolation is somewhat tricky, we clean tables directly
        # if needed, but for simple tests we'll just yield the session.
        yield session
    finally:
        session.close()


@pytest.fixture
def clean_db(db_session: Session) -> Generator[Session, None, None]:
    """Provide a completely clean database state for a test."""
    from app.db.models.alarm import Alarm
    from app.db.models.ingestion_batch import IngestionBatch
    from app.db.models.alarm_rejection import AlarmRejection

    # Delete all data
    db_session.query(AlarmRejection).delete()
    db_session.query(Alarm).delete()
    db_session.query(IngestionBatch).delete()
    db_session.commit()
    
    yield db_session


@pytest_asyncio.fixture
async def async_client(db_session: Session) -> AsyncGenerator[AsyncClient, None]:
    """Provide an AsyncClient for testing the FastAPI app with the test database."""

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
