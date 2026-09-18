from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

try:
    from itip_backend.core.config import settings
except ImportError:  # pragma: no cover
    from core.config import settings

engine = create_engine(
    settings.sqlalchemy_database_uri,
    pool_pre_ping=True,
    pool_recycle=1800,
    connect_args={"connect_timeout": 5},
)
SQLAlchemyInstrumentor().instrument(engine=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
