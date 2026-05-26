import re
import time

from pymongo.errors import OperationFailure, WriteError


THROTTLE_CODES = {16500, 429}


def is_throttle_error(exc: Exception) -> bool:
    code = getattr(exc, "code", None)
    if code in THROTTLE_CODES:
        return True
    message = str(exc).lower()
    return "retryafterms=" in message or "too many requests" in message or "429" in message


def retry_sleep_seconds(exc: Exception, attempt: int) -> float:
    match = re.search(r"RetryAfterMs=(\d+)", str(exc))
    if match:
        return max(int(match.group(1)) / 1000.0, 0.05)
    return min(2**attempt, 30)


def run_with_cosmos_retry(fn, max_retries: int = 10):
    attempt = 0
    while True:
        try:
            return fn()
        except (WriteError, OperationFailure) as exc:
            if not is_throttle_error(exc) or attempt >= max_retries:
                raise
            time.sleep(retry_sleep_seconds(exc, attempt))
            attempt += 1
