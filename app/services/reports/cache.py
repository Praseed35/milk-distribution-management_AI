import hashlib
import os
import time


CACHE_ENABLED = os.getenv("REPORT_CACHE_DISABLED", "0") != "1"


class ReportCache:
    def __init__(self):
        self._store: dict[str, tuple[float, object]] = {}

    def _make_key(self, report_type: str, params: dict) -> str:
        raw = f"{report_type}:{sorted(params.items())}"
        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, key: str):
        if not CACHE_ENABLED:
            return None
        if key in self._store:
            expires, data = self._store[key]
            if time.time() < expires:
                return data
            del self._store[key]
        return None

    def set(self, key: str, data, ttl: int = 300):
        if not CACHE_ENABLED:
            return
        self._store[key] = (time.time() + ttl, data)

    def invalidate(self, pattern: str | None = None):
        if pattern is None:
            self._store.clear()
        else:
            self._store = {k: v for k, v in self._store.items() if not k.startswith(pattern)}


report_cache = ReportCache()
