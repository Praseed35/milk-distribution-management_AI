import hashlib
import time


class ReportCache:
    def __init__(self):
        self._store: dict[str, tuple[float, object]] = {}

    def _make_key(self, report_type: str, params: dict) -> str:
        raw = f"{report_type}:{sorted(params.items())}"
        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, key: str):
        if key in self._store:
            expires, data = self._store[key]
            if time.time() < expires:
                return data
            del self._store[key]
        return None

    def set(self, key: str, data, ttl: int = 300):
        self._store[key] = (time.time() + ttl, data)

    def invalidate(self, pattern: str | None = None):
        if pattern is None:
            self._store.clear()
        else:
            self._store = {k: v for k, v in self._store.items() if not k.startswith(pattern)}


report_cache = ReportCache()
