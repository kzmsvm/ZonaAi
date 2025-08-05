import os
import time
from collections import defaultdict
from fastapi import Header, HTTPException, Request

API_KEY = os.getenv("API_KEY", "test-key")
API_KEY_HEADER = "X-API-Key"


class RateLimiter:
    def __init__(self, limit: int, window: int):
        self.limit = limit
        self.window = window
        self.calls: dict[str, list[float]] = defaultdict(list)

    async def __call__(self, request: Request) -> None:
        client = request.client.host if request.client else "anonymous"
        now = time.time()
        calls = [t for t in self.calls[client] if now - t < self.window]
        if len(calls) >= self.limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        calls.append(now)
        self.calls[client] = calls


def verify_api_key(x_api_key: str = Header(None, alias=API_KEY_HEADER)) -> None:
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


limiter = RateLimiter(limit=100, window=60)
