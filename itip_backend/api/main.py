from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import os
import csv
import io
from urllib.request import urlopen


try:
    from itip_backend.api.routers import entities, health
    from itip_backend.core.config import settings
    from itip_backend.core.tracing import configure_tracing
    from itip_backend.db.models import User
    from itip_backend.db.session import get_db
    from itip_backend.core.security import verify_password, create_access_token
except ImportError:  # pragma: no cover
    from api.routers import entities, health
    from core.config import settings
    from core.tracing import configure_tracing
    from db.models import User
    from db.session import get_db
    from core.security import verify_password, create_access_token


# --------------------------------------------------
# Configuration
# --------------------------------------------------

configure_tracing()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


FastAPIInstrumentor.instrument_app(app)


# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/", tags=["Meta"])
def root() -> dict:
    return {
        "service": settings.PROJECT_NAME,
        "status": "ok"
    }


# --------------------------------------------------
# Health
# --------------------------------------------------

app.include_router(
    health.router,
    tags=["Health"]
)


# --------------------------------------------------
# Entities
# --------------------------------------------------

app.include_router(
    entities.router,
    prefix=f"{settings.API_V1_STR}/entities",
    tags=["Entities"]
)


# --------------------------------------------------
# Authentication
# --------------------------------------------------

@app.post("/token", tags=["Authentication"])
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.username == form_data.username)
        .first()
    )

    if not user or not verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# --------------------------------------------------
# NASA FIRMS
# --------------------------------------------------

@app.get("/v1/firms", tags=["NASA FIRMS"])
def get_firms():

    # Get NASA FIRMS API key from environment variable
    api_key = os.getenv("FIRMS_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="FIRMS_API_KEY is not configured"
        )

    # India bounding box
    # west, south, east, north
    area = "68,6,97,37"

    url = (
        "https://firms.modaps.eosdis.nasa.gov/"
        f"api/area/csv/{api_key}/"
        f"VIIRS_NOAA21_NRT/{area}/5"
    )

    try:
        # Request data from NASA FIRMS
        with urlopen(url, timeout=30) as response:
            csv_data = response.read().decode("utf-8")

        # Read CSV response
        reader = csv.DictReader(
            io.StringIO(csv_data)
        )

        fires = []

        for row in reader:

            try:
                fires.append({
                    "latitude": float(row["latitude"]),
                    "longitude": float(row["longitude"]),
                    "brightness": float(row["bright_ti4"]),
                    "confidence": row["confidence"],
                    "frp": float(row["frp"]),
                    "acq_date": row["acq_date"],
                    "acq_time": row["acq_time"],
                    "satellite": row["satellite"],
                    "instrument": row["instrument"],
                    "daynight": row["daynight"],
                })

            except (ValueError, KeyError):
                # Ignore invalid/incomplete rows
                continue

        return {
            "source": "NASA FIRMS",
            "sensor": "VIIRS_NOAA21_NRT",
            "count": len(fires),
            "fires": fires
        }

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"FIRMS request failed: {str(e)}"
        )


# --------------------------------------------------
# Run locally
# --------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )