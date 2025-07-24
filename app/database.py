from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_config

# Get configuration
config = get_config()

# Sync engine for migrations and some auth operations
sync_engine = create_engine(
    config.DATABASE_URL_SYNC,
    pool_size=config.POOL_SIZE,
    max_overflow=config.MAX_OVERFLOW,
    pool_timeout=config.POOL_TIMEOUT,
    pool_recycle=config.POOL_RECYCLE,
    pool_pre_ping=True,
    echo=config.SQLALCHEMY_ECHO
)

# Async engine for FastAPI
async_engine = create_async_engine(
    config.DATABASE_URL_ASYNC,
    pool_size=config.POOL_SIZE,
    max_overflow=config.MAX_OVERFLOW,
    pool_timeout=config.POOL_TIMEOUT,
    pool_recycle=config.POOL_RECYCLE,
    echo=config.SQLALCHEMY_ECHO
)

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Create base class for declarative models
Base = declarative_base()

# Dependency for sync database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency for async database sessions
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

# Additional utility functions for database operations
async def create_tables():
    """Create all database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables():
    """Drop all database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Health check function
async def check_db_health():
    """Check if database is accessible"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        return True
    except Exception:
        return False