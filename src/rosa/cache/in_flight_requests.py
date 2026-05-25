import threading
from typing import Any, Callable


class _PendingRequest:
    def __init__(self):
        self.event = threading.Event()
        self.result = None


class RequestCoalescer:
    """Coalesces in-flight identical requests to avoid duplicate work."""

    def __init__(self, window_ms: float = 50.0):
        self._window_ms = window_ms
        self._in_flight: dict[str, _PendingRequest] = {}
        self._lock = threading.Lock()

    def execute(self, key: str, operation: Callable[[], Any]) -> Any:
        """Execute operation, coalescing with any in-flight request for same key."""
        with self._lock:
            if key in self._in_flight:
                pending = self._in_flight[key]
                wait = True
            else:
                pending = _PendingRequest()
                self._in_flight[key] = pending
                wait = False

        if wait:
            pending.event.wait()
            return pending.result

        try:
            result = operation()
            with self._lock:
                pending.result = result
                pending.event.set()
                self._in_flight.pop(key, None)
            return result
        except Exception:
            with self._lock:
                pending.event.set()
                self._in_flight.pop(key, None)
            raise
