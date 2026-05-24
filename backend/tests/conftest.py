import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from server.database import Base, get_db
from server.main import app

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/shiguang_test"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_token(client: AsyncClient):
    # For testing, bypass WeChat and directly create a user
    from server.models.user import User
    from server.utils.security import create_access_token
    import uuid

    async with TestSessionLocal() as db:
        user = User(
            openid=f"test_{uuid.uuid4().hex[:8]}",
            nickname="测试用户",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        token = create_access_token({"sub": str(user.id)})
        return token, user.id