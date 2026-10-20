from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from backend.core.config import config

is_sqlite = config.DATABASE_URL.startswith("sqlite")

connect_args = {}
engine_kwargs = {"pool_pre_ping": True}

if is_sqlite:
    connect_args["check_same_thread"] = False
    connect_args["timeout"] = 30.0
else:
    # Production connection pooling settings for PostgreSQL or external RDBMS
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 1800,
    })

engine = create_engine(
    config.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

if is_sqlite:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """
        Enforce SQLite reliability pragmas:
        - foreign_keys=ON: Guarantees referential integrity
        - journal_mode=WAL: Permits concurrent reading and writing without database locks
        - busy_timeout=10000: Waits up to 10 seconds for locks to clear before raising OperationalError
        - synchronous=NORMAL: Optimal balance of data safety and high throughput in WAL mode
        """
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=10000")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency that provides a database session and ensures it is safely closed.
    Use this to yield DB sessions in API endpoints or services.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def transactional_session():
    """
    Context manager providing a transactional scope around a series of operations.
    Automatically commits on normal completion or rolls back upon any uncaught exception.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
