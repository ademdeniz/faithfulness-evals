"""Bounded retries for transient provider failures."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from collections.abc import Awaitable, Callable
from typing import TypeVar


T = TypeVar("T")
logger = logging.getLogger("faithfulness.retry")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
    logger.propagate = False


def is_retryable(error: BaseException) -> bool:
    status_code = getattr(error, "status_code", None)
    return isinstance(error, (TimeoutError, ConnectionError)) or status_code == 429 or (
        isinstance(status_code, int) and status_code >= 500
    )


def retry_call(
    operation: Callable[[], T],
    *,
    attempts: int = 3,
    delay_seconds: float = 1.0,
    operation_name: str = "provider_call",
) -> T:
    if attempts < 1 or delay_seconds < 0:
        raise ValueError("attempts must be positive and delay_seconds cannot be negative")
    for attempt in range(attempts):
        try:
            return operation()
        except Exception as error:
            if not is_retryable(error) or attempt == attempts - 1:
                raise
            logger.warning(
                json.dumps(
                    {
                        "event": "retry",
                        "operation": operation_name,
                        "attempt": attempt + 1,
                        "next_attempt": attempt + 2,
                        "error_type": type(error).__name__,
                    }
                )
            )
            time.sleep(delay_seconds * (2**attempt))
    raise AssertionError("retry loop did not return or raise")


async def async_retry_call(
    operation: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    delay_seconds: float = 1.0,
    timeout_seconds: float | None = None,
    operation_name: str = "provider_call",
) -> T:
    if attempts < 1 or delay_seconds < 0:
        raise ValueError("attempts must be positive and delay_seconds cannot be negative")
    for attempt in range(attempts):
        try:
            call = operation()
            return await (
                asyncio.wait_for(call, timeout_seconds)
                if timeout_seconds is not None
                else call
            )
        except Exception as error:
            if not is_retryable(error) or attempt == attempts - 1:
                raise
            logger.warning(
                json.dumps(
                    {
                        "event": "retry",
                        "operation": operation_name,
                        "attempt": attempt + 1,
                        "next_attempt": attempt + 2,
                        "error_type": type(error).__name__,
                    }
                )
            )
            await asyncio.sleep(delay_seconds * (2**attempt))
    raise AssertionError("retry loop did not return or raise")
