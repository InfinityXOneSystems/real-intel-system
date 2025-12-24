import os
from typing import Optional

def init_tracing(service_name: str = "real-estate-telephony"):
    # Local stub: initialize OpenTelemetry exporters if available.
    # In CI/dry-run this will be a noop.
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

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
