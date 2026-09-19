from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

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


configure_tracing()

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


FastAPIInstrumentor.instrument_app(app)


@app.get("/", tags=["Meta"])
def root() -> dict:
    return {
        "service": settings.PROJECT_NAME,
        "status": "ok"
    }


app.include_router(health.router, tags=["Health"])

app.include_router(
    entities.router,
    prefix=f"{settings.API_V1_STR}/entities",
    tags=["Entities"]
)


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )