from functools import wraps
from flask import request, jsonify
import time
import logging
from threading import Lock
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = Lock()

    def _cleanup_old_requests(self, key: str, period: int):
        current_time = time.time()
        with self.lock:
            self.requests[key] = [req_time for req_time in self.requests[key]
                                if current_time - req_time < period]

    def check_rate_limit(self, key: str, calls: int, period: int) -> bool:
        self._cleanup_old_requests(key, period)
        with self.lock:
            if len(self.requests[key]) >= calls:
                return False
            self.requests[key].append(time.time())
            return True

def rate_limit(calls: int = 60, period: int = 60):
    limiter = RateLimiter()
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            key = f"{request.remote_addr}:{f.__name__}"
            
            if not limiter.check_rate_limit(key, calls, period):
                logger.warning(f"Rate limit exceeded for {key}")
                response = {
                    'error': 'Rate Limit Exceeded',
                    'message': f'Please wait before making another request. Maximum {calls} calls per {period} seconds.'
                }
                return jsonify(response), 429
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator