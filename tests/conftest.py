from typing import Dict, Generator

import pytest

from app.db.database import SessionLocal

@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()