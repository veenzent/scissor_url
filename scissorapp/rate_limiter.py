from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps

class RateLimit:
    """
    Rate limiting class to store and manage rate limits for different endpoints.
    """

    def __init__(self, limit, interval):
        self.limit = limit
        self.interval = interval
        self.data = defaultdict(lambda: {"requests": 0, "last_accessed": datetime.min})

    def check(self, request: Request):
        """
        Checks if the request exceeds the rate limit for the endpoint.

        Args:
            request: The FastAPI request object.

        Raises:
            HTTPException: If the rate limit is exceeded.
        """

        endpoint = request.url.path
        now = datetime.utcnow()
        last_accessed = self.data[endpoint]["last_accessed"]
        requests = self.data[endpoint]["requests"]

        if now - last_accessed > self.interval:
            # Reset counter if interval has passed
            self.data[endpoint]["requests"] = 0
            self.data[endpoint]["last_accessed"] = now
        else:
            requests += 1

        if requests > self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Please try again in {self.interval.total_seconds():.2f} seconds.",
            )

        self.data[endpoint]["requests"] = requests

rate_limit = RateLimit(limit=10, interval=timedelta(seconds=60))  # Example configuration

def rate_limiter(limit=None, interval=None):
    """
    Custom decorator to apply rate limits to endpoints.

    Args:
        limit: Optional rate limit (overrides default).
        interval: Optional time interval (overrides default).

    Returns:
        A decorator function.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            if limit is not None or interval is not None:
                limiter = RateLimit(limit=limit, interval=interval)
            else:
                limiter = rate_limit  # Use default rate limiter

            limiter.check(request)
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
