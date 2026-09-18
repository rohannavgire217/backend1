from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

try:
    from itip_backend.core.config import settings
except ImportError:  # pragma: no cover
    from core.config import settings


def configure_tracing() -> None:
    provider = TracerProvider(
        resource=Resource.create({"service.name": settings.OTEL_SERVICE_NAME})
    )

    if settings.OTEL_EXPORTER_OTLP_ENDPOINT:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
            )
        )
    if settings.OTEL_CONSOLE_EXPORTER:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
