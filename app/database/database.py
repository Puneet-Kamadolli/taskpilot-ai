from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import DATABASE_URL

# SQLite specific connection configuration
connect_args = (
    {"check_same_thread":False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    )

# Create database session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()

# FastAPI database dependency
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()
