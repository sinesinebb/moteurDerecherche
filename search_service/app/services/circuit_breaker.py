# services/circuit_breaker.py
import asyncio
from typing import Any, Callable
from functools import wraps

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = None
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == "OPEN":
            if self._timeout_elapsed():
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        self.failures = 0
        self.state = "CLOSED"
        self.last_failure_time = None
    
    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = asyncio.get_event_loop().time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
    
    def _timeout_elapsed(self) -> bool:
        if not self.last_failure_time:
            return False
        return (asyncio.get_event_loop().time() - self.last_failure_time) > self.timeout

# Application aux clients
user_circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30)
indexing_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)