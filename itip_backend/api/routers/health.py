from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

try:
    from itip_backend.db.session import get_db
except ImportError:  # pragma: no cover
    from db.session import get_db

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "ITIP Backend"}


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not ready",
        ) from exc

    return {"status": "ready", "dependencies": {"database": "ok"}}
