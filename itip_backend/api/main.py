from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

try:
    from itip_backend.api.routers import entities, health
    from itip_backend.core.config import settings
    from itip_backend.core.tracing import configure_tracing
except ImportError:  # pragma: no cover
    from api.routers import entities, health
    from core.config import settings
    from core.tracing import configure_tracing

configure_tracing()
app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")
FastAPIInstrumentor.instrument_app(app)


@app.get("/", tags=["Meta"])
def root() -> dict:
    return {"service": settings.PROJECT_NAME, "status": "ok"}


app.include_router(health.router, tags=["Health"])
app.include_router(entities.router, prefix=f"{settings.API_V1_STR}/entities", tags=["Entities"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)