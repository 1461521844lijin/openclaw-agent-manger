"""Database connection and session management"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all models"""

    pass


async def init_db():
    """Initialize database tables and seed data"""
    from .models import Role
    from .services.seed_data import BUILTIN_ROLES

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed builtin roles
    async with async_session_maker() as session:
        for role_data in BUILTIN_ROLES:
            # Check if role already exists
            result = await session.execute(
                select(Role).where(Role.name_en == role_data["name_en"])
            )
            existing_role = result.scalar_one_or_none()
            if not existing_role:
                role = Role(**role_data)
                session.add(role)
        await session.commit()


async def get_session() -> AsyncSession:
    """Get database session"""
    async with async_session_maker() as session:
        yield session
