"""OpenTelemetry initialization helper for the autonomy services.

Usage: call `init_tracing(service_name)` at process startup. Expects
env vars to configure exporter (OTEL_EXPORTER_OTLP_ENDPOINT, etc.).
"""

import logging
import os

logger = logging.getLogger(__name__)


def init_tracing(service_name: str = "infinity-autonomy") -> None:
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import \
            OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if not endpoint:
            logger.info("No OTLP endpoint configured; tracing will be no-op")
            return

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        span_exporter = OTLPSpanExporter(endpoint=endpoint)
        processor = BatchSpanProcessor(span_exporter)
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        logger.info("OpenTelemetry initialized for %s -> %s", service_name, endpoint)
    except Exception:
        logger.exception(
            "Failed to initialize OpenTelemetry. Continuing without tracing."
        )


import os
from typing import Optional


def init_tracing(service_name: str = "real-estate-telephony"):
    # Local stub: initialize OpenTelemetry exporters if available.
    # In CI/dry-run this will be a noop.
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                                    ConsoleSpanExporter)

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        tracer = trace.get_tracer(__name__)
        return tracer
    except Exception:
        # opentelemetry not installed — return a dummy tracer
        class DummyTracer:
            def start_as_current_span(self, name):
                class Ctx:
                    def __enter__(self):
                        return None

                    def __exit__(self, exc_type, exc, tb):
                        return False

                return Ctx()

        return DummyTracer()
