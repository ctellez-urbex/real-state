"""Concurrency utilities for thread management and recursive operations."""

import asyncio
import concurrent.futures
import threading
from typing import Any, Callable, Dict, List, Optional, TypeVar
from functools import wraps
from dataclasses import dataclass
from app.core.logging import get_logger, LoggerMixin
from app.core.patterns import RetryDecorator, CircuitBreaker

logger = get_logger(__name__)

T = TypeVar('T')
R = TypeVar('R')


class ThreadPoolManager(LoggerMixin):
    """Thread pool manager for concurrent operations."""
    
    def __init__(self, max_workers: Optional[int] = None):
        """Initialize thread pool manager.
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers
        self._executor: Optional[concurrent.futures.ThreadPoolExecutor] = None
        self._lock = threading.Lock()
    
    def __enter__(self):
        """Context manager entry."""
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._executor:
            self._executor.shutdown(wait=True)
    
    def submit(self, func: Callable[..., R], *args, **kwargs) -> concurrent.futures.Future[R]:
        """Submit a task to the thread pool.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Future object for the task
        """
        if not self._executor:
            raise RuntimeError("ThreadPoolManager not initialized. Use as context manager.")
        
        return self._executor.submit(func, *args, **kwargs)
    
    def map(self, func: Callable[..., R], iterable: List[Any]) -> List[R]:
        """Map function over iterable using thread pool.
        
        Args:
            func: Function to apply
            iterable: Items to process
            
        Returns:
            List of results
        """
        if not self._executor:
            raise RuntimeError("ThreadPoolManager not initialized. Use as context manager.")
        
        return list(self._executor.map(func, iterable))


class AsyncTaskManager(LoggerMixin):
    """Async task manager for concurrent operations."""
    
    def __init__(self, max_concurrent: int = 10):
        """Initialize async task manager.
        
        Args:
            max_concurrent: Maximum concurrent tasks
        """
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute_with_semaphore(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with semaphore control.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        async with self._semaphore:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, func, *args, **kwargs)
    
    async def gather_with_semaphore(self, tasks: List[Callable], *args, **kwargs) -> List[Any]:
        """Gather multiple tasks with semaphore control.
        
        Args:
            tasks: List of functions to execute
            *args: Common arguments for all tasks
            **kwargs: Common keyword arguments for all tasks
            
        Returns:
            List of results
        """
        async def execute_task(task):
            return await self.execute_with_semaphore(task, *args, **kwargs)
        
        return await asyncio.gather(*[execute_task(task) for task in tasks])


@dataclass
class RecursiveResult:
    """Result container for recursive operations."""
    value: Any
    depth: int
    path: List[str]
    metadata: Dict[str, Any]


class RecursionManager(LoggerMixin):
    """Manager for recursive operations with safety controls."""
    
    def __init__(self, max_depth: int = 100, max_iterations: int = 1000):
        """Initialize recursion manager.
        
        Args:
            max_depth: Maximum recursion depth
            max_iterations: Maximum iterations to prevent infinite loops
        """
        self.max_depth = max_depth
        self.max_iterations = max_iterations
        self._iteration_count = 0
        self._call_stack: List[str] = []
    
    def reset(self) -> None:
        """Reset recursion state."""
        self._iteration_count = 0
        self._call_stack.clear()
    
    def recursive_function(self, func: Callable) -> Callable:
        """Decorator for recursive functions with safety controls.
        
        Args:
            func: Function to decorate
            
        Returns:
            Decorated function with safety controls
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            self._iteration_count += 1
            
            if self._iteration_count > self.max_iterations:
                raise RecursionError(f"Maximum iterations ({self.max_iterations}) exceeded")
            
            # Add function name to call stack
            self._call_stack.append(func.__name__)
            
            try:
                # Check depth
                if len(self._call_stack) > self.max_depth:
                    raise RecursionError(f"Maximum depth ({self.max_depth}) exceeded")
                
                result = func(*args, **kwargs)
                return result
            
            finally:
                # Remove function name from call stack
                if self._call_stack:
                    self._call_stack.pop()
        
        return wrapper
    
    def safe_recursion(self, func: Callable, *args, **kwargs) -> RecursiveResult:
        """Execute recursive function with safety controls.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            RecursiveResult with value and metadata
        """
        self.reset()
        
        try:
            result = func(*args, **kwargs)
            return RecursiveResult(
                value=result,
                depth=len(self._call_stack),
                path=self._call_stack.copy(),
                metadata={
                    "iterations": self._iteration_count,
                    "max_depth": self.max_depth,
                    "max_iterations": self.max_iterations
                }
            )
        except RecursionError as e:
            self.logger.error("Recursion limit exceeded", error=str(e))
            raise


class ConcurrentProcessor(LoggerMixin):
    """Processor for concurrent operations with error handling."""
    
    def __init__(self, max_workers: int = 4, timeout: Optional[float] = None):
        """Initialize concurrent processor.
        
        Args:
            max_workers: Maximum number of worker threads
            timeout: Timeout for operations in seconds
        """
        self.max_workers = max_workers
        self.timeout = timeout
        self.retry_decorator = RetryDecorator(max_attempts=3)
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
    
    def process_batch(self, items: List[T], processor: Callable[[T], R]) -> List[R]:
        """Process items in batch using thread pool.
        
        Args:
            items: Items to process
            processor: Processing function
            timeout: Timeout for the entire batch
            
        Returns:
            List of processed results
        """
        with ThreadPoolManager(max_workers=self.max_workers) as pool:
            futures = [pool.submit(processor, item) for item in items]
            
            results = []
            for future in concurrent.futures.as_completed(futures, timeout=self.timeout):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error("Error processing item", error=str(e))
                    results.append(None)
            
            return results
    
    def process_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Process function with retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        retry_func = self.retry_decorator(func)
        return self.circuit_breaker.call(retry_func, *args, **kwargs)


class ThreadSafeCache(LoggerMixin):
    """Thread-safe cache implementation."""
    
    def __init__(self, max_size: int = 1000):
        """Initialize thread-safe cache.
        
        Args:
            max_size: Maximum cache size
        """
        self.max_size = max_size
        self._cache: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._access_count: Dict[str, int] = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        with self._lock:
            if key in self._cache:
                self._access_count[key] = self._access_count.get(key, 0) + 1
                return self._cache[key]
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            if len(self._cache) >= self.max_size:
                self._evict_least_used()
            
            self._cache[key] = value
            self._access_count[key] = 0
    
    def _evict_least_used(self) -> None:
        """Evict least used item from cache."""
        if not self._access_count:
            # If no access count, remove first item
            key_to_remove = next(iter(self._cache))
        else:
            key_to_remove = min(self._access_count, key=self._access_count.get)
        
        del self._cache[key_to_remove]
        del self._access_count[key_to_remove]
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._access_count.clear()
    
    def size(self) -> int:
        """Get current cache size.
        
        Returns:
            Number of cached items
        """
        with self._lock:
            return len(self._cache)


def async_retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator for async retry logic.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds
        
    Returns:
        Decorated async function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
            
            raise last_exception
        
        return wrapper
    return decorator


def thread_safe(func: Callable) -> Callable:
    """Decorator to make function thread-safe.
    
    Args:
        func: Function to make thread-safe
        
    Returns:
        Thread-safe function
    """
    lock = threading.Lock()
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        with lock:
            return func(*args, **kwargs)
    
    return wrapper 