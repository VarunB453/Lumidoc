"""OpenTelemetry setup for distributed tracing and metrics.

This module initializes OpenTelemetry tracing when OTEL_ENABLED=true.
In development/test, tracing is disabled by default.
"""
from __future__ import annotations

import os
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("telemetry")

_tracer: Any = None


def setup_telemetry() -> None:
    """Initialize OpenTelemetry SDK if enabled via environment."""
    global _tracer

    otel_enabled = os.getenv("OTEL_ENABLED", "false").lower() == "true"
    if not otel_enabled:
        logger.info("telemetry_disabled")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create(
            {
                "service.name": settings.APP_NAME,
                "service.version": settings.APP_VERSION,
                "deployment.environment": settings.APP_ENV,
            }
        )

        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        _tracer = trace.get_tracer(settings.APP_NAME)
        logger.info("telemetry_initialized", endpoint=exporter._endpoint)

    except ImportError:
        logger.warning("telemetry_packages_not_installed")
    except Exception as e:
        logger.warning("telemetry_setup_failed", error=str(e))


def get_tracer() -> Any:
    """Return the configured tracer or None if telemetry is disabled."""
    return _tracer


def instrument_app(app: Any) -> None:
    """Instrument a FastAPI app with OpenTelemetry (if available)."""
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)
        logger.info("fastapi_instrumented")
    except ImportError:
        pass
    except Exception as e:
        logger.warning("fastapi_instrumentation_failed", error=str(e))
