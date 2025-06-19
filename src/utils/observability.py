"""Simple Langfuse observability for AI agents."""

import base64
import logging
import os
from langfuse import get_client
import logfire

from src.config import settings

logger = logging.getLogger(__name__)


def configure_observability():
    """Configure logfire and Langfuse OTEL integration."""
    logfire.configure(
        service_name="Content Multi-Agent Pipeline",
        send_to_logfire=False,
    )

    # Check if all Langfuse config is present
    if (
        settings.langfuse_public_key
        and settings.langfuse_secret_key
        and settings.langfuse_host
    ):
        auth = base64.b64encode(
            f"{settings.langfuse_public_key}:{settings.langfuse_secret_key}".encode()
        ).decode()
        headers = {"Authorization": f"Basic {auth}"}
        endpoint = f"{settings.langfuse_host}/api/public/otel"
        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = endpoint
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = ",".join(
            f"{k}={v}" for k, v in headers.items()
        )
        logger.info("Langfuse OTEL integration configured")
    else:
        logger.warning(
            "Langfuse environment variables not found - OTEL integration disabled"
        )


def get_langfuse():
    """Get Langfuse client - uses environment variables for configuration."""
    try:
        return get_client()
    except Exception as e:
        logger.warning(f"Langfuse not available: {e}")
        return None


def flush_traces():
    """Flush traces at the end of operations."""
    try:
        client = get_langfuse()
        if client:
            client.flush()
    except Exception as e:
        logger.warning(f"Failed to flush traces: {e}")
