from __future__ import annotations

import functools
import inspect
import os
import time
from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Callable, Iterator


DEFAULT_LANGFUSE_HOST = "http://localhost:3000"

_LANGFUSE_CLIENT: Any | None = None
_LANGFUSE_UNAVAILABLE = False


def get_langfuse_client() -> Any | None:
    """Return a configured Langfuse client, or None when tracing is not configured."""
    global _LANGFUSE_CLIENT, _LANGFUSE_UNAVAILABLE

    if _LANGFUSE_CLIENT is not None:
        return _LANGFUSE_CLIENT
    if _LANGFUSE_UNAVAILABLE:
        return None

    host = os.environ.setdefault("LANGFUSE_HOST", DEFAULT_LANGFUSE_HOST)
    os.environ.setdefault("LANGFUSE_BASE_URL", host)

    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    if not public_key or not secret_key:
        return None

    try:
        from langfuse import Langfuse
    except ImportError:
        _LANGFUSE_UNAVAILABLE = True
        return None

    try:
        _LANGFUSE_CLIENT = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
        )
    except Exception:
        _LANGFUSE_UNAVAILABLE = True
        return None
    return _LANGFUSE_CLIENT


def _safe_value(value: Any, depth: int = 0) -> Any:
    if depth > 3:
        return repr(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value):
        return _safe_value(asdict(value), depth + 1)
    if isinstance(value, dict):
        return {
            str(key): _safe_value(item, depth + 1)
            for key, item in list(value.items())[:50]
        }
    if isinstance(value, (list, tuple, set)):
        return [_safe_value(item, depth + 1) for item in list(value)[:50]]
    shape = getattr(value, "shape", None)
    if shape is not None:
        return {"type": type(value).__name__, "shape": tuple(shape)}
    return repr(value)


def _function_inputs(func: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    skip_names = {"self", "cls", "model", "processor"}
    try:
        bound = inspect.signature(func).bind_partial(*args, **kwargs)
        bound.apply_defaults()
    except (TypeError, ValueError):
        return {
            "args": _safe_value(args),
            "kwargs": _safe_value(kwargs),
        }
    return {
        name: _safe_value(value)
        for name, value in bound.arguments.items()
        if name not in skip_names
    }


def _update_observation(observation: Any, **kwargs: Any) -> None:
    try:
        observation.update(**kwargs)
    except Exception:
        return


def _supports_observations(client: Any) -> bool:
    return hasattr(client, "start_as_current_observation")


def trace_step(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Wrap a function in a Langfuse span with input, output, latency, and errors."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            client = get_langfuse_client()
            if client is None or not _supports_observations(client):
                return func(*args, **kwargs)

            start = time.perf_counter()
            inputs = _function_inputs(func, args, kwargs)
            try:
                manager = client.start_as_current_observation(
                    as_type="span",
                    name=name,
                    input=inputs,
                )
            except Exception:
                return func(*args, **kwargs)

            with manager as span:
                try:
                    result = func(*args, **kwargs)
                except Exception as exc:
                    latency_ms = (time.perf_counter() - start) * 1000
                    _update_observation(
                        span,
                        metadata={
                            "latency_ms": round(latency_ms, 3),
                            "error_type": type(exc).__name__,
                            "error": str(exc),
                        },
                        level="ERROR",
                        status_message=str(exc),
                    )
                    raise

                latency_ms = (time.perf_counter() - start) * 1000
                _update_observation(
                    span,
                    output=_safe_value(result),
                    metadata={"latency_ms": round(latency_ms, 3)},
                )
                return result

        return wrapper

    return decorator


@contextmanager
def trace_query(query: str, metadata: dict[str, Any] | None = None) -> Iterator[Any | None]:
    """Create one parent trace for a user query."""
    client = get_langfuse_client()
    if client is None or not _supports_observations(client):
        yield None
        return

    start = time.perf_counter()
    trace_metadata = {"component": "rag_pipeline", **(metadata or {})}
    try:
        manager = client.start_as_current_observation(
            as_type="span",
            name="rag.query",
            input={"query": query},
            metadata=trace_metadata,
        )
    except Exception:
        yield None
        return

    with manager as span:
        try:
            yield span
        except Exception as exc:
            latency_ms = (time.perf_counter() - start) * 1000
            _update_observation(
                span,
                metadata={
                    **trace_metadata,
                    "latency_ms": round(latency_ms, 3),
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
                level="ERROR",
                status_message=str(exc),
            )
            raise
        else:
            latency_ms = (time.perf_counter() - start) * 1000
            _update_observation(
                span,
                metadata={
                    **trace_metadata,
                    "latency_ms": round(latency_ms, 3),
                },
            )


def log_retrieval(
    query: str,
    retrieved_docs: list[Any],
    scores: list[float],
    latency_ms: float,
) -> None:
    """Log a retrieval observation with query, result count, scores, and latency."""
    client = get_langfuse_client()
    if client is None or not _supports_observations(client):
        return

    metadata = {
        "latency_ms": round(latency_ms, 3),
        "doc_count": len(retrieved_docs),
        "top_k_scores": [round(float(score), 6) for score in scores[:20]],
    }
    try:
        with client.start_as_current_observation(
            as_type="retriever",
            name="retrieval",
            input={"query": query},
            output={"documents": _safe_value(retrieved_docs)},
            metadata=metadata,
        ):
            return
    except Exception:
        return


def log_generation(
    prompt: str,
    response: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    first_token_latency_ms: float | None,
    total_latency_ms: float,
) -> None:
    """Log a generation observation with model, token usage, TTFT, and latency."""
    client = get_langfuse_client()
    if client is None or not _supports_observations(client):
        return

    usage_details = {
        "input": int(input_tokens),
        "output": int(output_tokens),
        "total": int(input_tokens) + int(output_tokens),
    }
    metadata = {
        "first_token_latency_ms": (
            round(first_token_latency_ms, 3)
            if first_token_latency_ms is not None
            else None
        ),
        "total_latency_ms": round(total_latency_ms, 3),
        "input_tokens": int(input_tokens),
        "output_tokens": int(output_tokens),
        "total_tokens": int(input_tokens) + int(output_tokens),
    }
    try:
        with client.start_as_current_observation(
            as_type="generation",
            name="generation",
            input=prompt,
            output=response,
            metadata=metadata,
            model=model,
            usage_details=usage_details,
        ):
            return
    except Exception:
        return


def flush_traces() -> None:
    client = get_langfuse_client()
    if client is None:
        return
    try:
        client.flush()
    except Exception:
        return
