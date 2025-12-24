"""Lightweight tracing span helper that no-ops when OTLP exporter not configured.

Usage:
    from tracing_span import tracer
    with tracer.start_span('my-op'):
        do_work()
"""

import logging
import os

logger = logging.getLogger(__name__)


class _NoopSpan:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        return False


class Tracer:
    def __init__(self):
        self._enabled = False
        self._tracer = None
        if os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
            try:
                from opentelemetry import trace
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
                    OTLPSpanExporter
                from opentelemetry.sdk.resources import Resource
                from opentelemetry.sdk.trace import TracerProvider
                from opentelemetry.sdk.trace.export import BatchSpanProcessor

                provider = TracerProvider(
                    resource=Resource.create({"service.name": "infinity-autonomy"})
                )
                exporter = OTLPSpanExporter()
                provider.add_span_processor(BatchSpanProcessor(exporter))
                trace.set_tracer_provider(provider)
                self._tracer = trace.get_tracer(__name__)
                self._enabled = True
            except Exception:
                logger.exception("Failed to initialize OTLP exporter; tracing disabled")
                self._enabled = False

    def start_span(self, name: str):
        if not self._enabled or self._tracer is None:
            return _NoopSpan()
        return self._tracer.start_as_current_span(name)


tracer = Tracer()
