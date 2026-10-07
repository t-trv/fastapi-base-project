import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models.base import Base
from app.config.database import get_db

# Engine SQLite in-memory dùng cho test
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session", autouse=True)
def mock_external_services(monkeypatch_session=None):
    """
    Mock Redis và Scheduler để test chạy độc lập không phụ thuộc service ngoài.
    """
    from unittest.mock import AsyncMock, MagicMock
    import app.main as main_module

    # Mock lifespan events (Redis & Scheduler)
    main_module.init_redis = AsyncMock()
    main_module.close_redis = AsyncMock()
    main_module.setup_scheduler = MagicMock()
    main_module.shutdown_scheduler = MagicMock()


@pytest.fixture(autouse=True)
async def setup_db():
    """
    Tạo schema trước mỗi test và dọn sạch sau khi test xong.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture cung cấp session DB test cho các test cases trực tiếp với repository/service.
    """
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture AsyncClient gửi HTTP request trực tiếp tới FastAPI app với DB đã override.
    """
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
