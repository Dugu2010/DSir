from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.config import get_settings
import structlog
import time

settings = get_settings()
logger = structlog.get_logger()

# Convert Render's postgres:// to postgresql+psycopg:// for SQLAlchemy
_db_url = settings.DATABASE_URL
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql+psycopg://", 1)
elif _db_url.startswith("postgresql://"):
    _db_url = _db_url.replace("postgresql://", "postgresql+psycopg://", 1)

# Main engine (for writes)
engine = create_async_engine(
    _db_url,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# Read replica engine (if configured)
read_replica_engine = None
if settings.DATABASE_READ_REPLICA_URL:
    _read_replica_url = settings.DATABASE_READ_REPLICA_URL
    if _read_replica_url.startswith("postgres://"):
        _read_replica_url = _read_replica_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif _read_replica_url.startswith("postgresql://"):
        _read_replica_url = _read_replica_url.replace("postgresql://", "postgresql+psycopg://", 1)
    
    read_replica_engine = create_async_engine(
        _read_replica_url,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_recycle=settings.DATABASE_POOL_RECYCLE,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# For read-only operations, we can use the read replica if available
def get_session_factory():
    """Get appropriate session factory based on operation type."""
    # In a more sophisticated implementation, we'd route based on operation
    # For now, we'll just return the main factory
    return async_session_factory

class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """Dependency that provides a database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection() -> bool:
    """Check if we can connect to the database."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def close_db_connection():
    """Close database connections."""
    await engine.dispose()
    if read_replica_engine:
        await read_replica_engine.dispose()


# Query monitoring middleware
class QueryMonitor:
    """Monitor database queries for slow performance."""
    
    @staticmethod
    async def execute_with_monitoring(conn, statement, parameters=None):
        """Execute a statement and log if it's slow."""
        start_time = time.time()
        try:
            result = await conn.execute(statement, parameters or {})
            elapsed = time.time() - start_time
            
            if elapsed > settings.DATABASE_SLOW_QUERY_THRESHOLD:
                logger.warning(
                    "slow_query_detected",
                    query=str(statement),
                    parameters=parameters,
                    duration=elapsed,
                    threshold=settings.DATABASE_SLOW_QUERY_THRESHOLD
                )
            
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                "query_execution_failed",
                query=str(statement),
                parameters=parameters,
                duration=elapsed,
                error=str(e)
            )
            raise
