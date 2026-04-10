import logging

from fastapi import FastAPI

from app.core.settings import settings

logger = logging.getLogger(__name__)


def configure_observability(app: FastAPI) -> None:
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    except Exception as exc:
        logger.warning("Prometheus instrumentation skipped: %s", exc)

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        tracer_provider = TracerProvider(
            resource=Resource.create({"service.name": settings.service_name})
        )
        exporter = OTLPSpanExporter(
            endpoint=f"{settings.otel_exporter_otlp_endpoint}/v1/traces"
        )
        tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(tracer_provider)

        FastAPIInstrumentor.instrument_app(app)
        RequestsInstrumentor().instrument()
    except Exception as exc:
        logger.warning("OpenTelemetry initialization skipped: %s", exc)
