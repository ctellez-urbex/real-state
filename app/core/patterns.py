"""Design patterns implementation for clean and reusable code."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from enum import Enum
from functools import wraps
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.logging import get_logger, LoggerMixin

logger = get_logger(__name__)

T = TypeVar('T')


class StrategyPattern:
    """Strategy pattern for interchangeable algorithms."""
    
    def __init__(self, strategy: 'Strategy'):
        """Initialize with a strategy.
        
        Args:
            strategy: Strategy implementation
        """
        self._strategy = strategy
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute the current strategy.
        
        Args:
            *args: Strategy arguments
            **kwargs: Strategy keyword arguments
            
        Returns:
            Strategy execution result
        """
        return self._strategy.execute(*args, **kwargs)
    
    def set_strategy(self, strategy: 'Strategy') -> None:
        """Change the current strategy.
        
        Args:
            strategy: New strategy implementation
        """
        self._strategy = strategy


class Strategy(ABC):
    """Abstract base class for strategies."""
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the strategy.
        
        Args:
            *args: Strategy arguments
            **kwargs: Strategy keyword arguments
            
        Returns:
            Strategy execution result
        """
        pass


class FactoryPattern:
    """Factory pattern for object creation."""
    
    _creators: Dict[str, Type] = {}
    
    @classmethod
    def register(cls, name: str, creator: Type) -> None:
        """Register a creator for a given name.
        
        Args:
            name: Name to register the creator under
            creator: Creator class or function
        """
        cls._creators[name] = creator
    
    @classmethod
    def create(cls, name: str, *args, **kwargs) -> Any:
        """Create an object using the registered creator.
        
        Args:
            name: Name of the registered creator
            *args: Creator arguments
            **kwargs: Creator keyword arguments
            
        Returns:
            Created object
            
        Raises:
            ValueError: If creator not found
        """
        creator = cls._creators.get(name)
        if not creator:
            raise ValueError(f"No creator registered for '{name}'")
        return creator(*args, **kwargs)


class RepositoryPattern(Generic[T]):
    """Repository pattern for data access abstraction."""
    
    def __init__(self, model: Type[T]):
        """Initialize repository with model type.
        
        Args:
            model: Model class type
        """
        self.model = model
    
    @abstractmethod
    async def get(self, id: Any) -> Optional[T]:
        """Get entity by ID.
        
        Args:
            id: Entity identifier
            
        Returns:
            Entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def list(self, **filters) -> List[T]:
        """List entities with optional filters.
        
        Args:
            **filters: Filter criteria
            
        Returns:
            List of entities
        """
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity.
        
        Args:
            entity: Entity to create
            
        Returns:
            Created entity
        """
        pass
    
    @abstractmethod
    async def update(self, id: Any, entity: T) -> Optional[T]:
        """Update an existing entity.
        
        Args:
            id: Entity identifier
            entity: Updated entity data
            
        Returns:
            Updated entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Delete an entity.
        
        Args:
            id: Entity identifier
            
        Returns:
            True if deleted, False otherwise
        """
        pass


class Singleton:
    """Singleton pattern implementation."""
    
    _instances: Dict[Type, Any] = {}
    
    def __new__(cls, *args, **kwargs):
        """Create or return existing instance.
        
        Returns:
            Singleton instance
        """
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]


class ObserverPattern:
    """Observer pattern for event handling."""
    
    def __init__(self):
        """Initialize observer pattern."""
        self._observers: List[callable] = []
    
    def attach(self, observer: callable) -> None:
        """Attach an observer.
        
        Args:
            observer: Observer function to attach
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: callable) -> None:
        """Detach an observer.
        
        Args:
            observer: Observer function to detach
        """
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
    
    def notify(self, *args, **kwargs) -> None:
        """Notify all observers.
        
        Args:
            *args: Arguments to pass to observers
            **kwargs: Keyword arguments to pass to observers
        """
        for observer in self._observers:
            try:
                observer(*args, **kwargs)
            except Exception as e:
                logger.error("Observer notification failed", error=str(e))


class CacheStrategy(Strategy):
    """Strategy for different caching approaches."""
    
    def __init__(self, cache_type: str = "memory"):
        """Initialize cache strategy.
        
        Args:
            cache_type: Type of cache to use
        """
        self.cache_type = cache_type
        self._cache: Dict[str, Any] = {}
    
    def execute(self, key: str, value: Any = None, ttl: int = 3600) -> Any:
        """Execute cache operation.
        
        Args:
            key: Cache key
            value: Value to cache (for set operations)
            ttl: Time to live in seconds
            
        Returns:
            Cached value or None
        """
        if value is not None:
            return self._set(key, value, ttl)
        return self._get(key)
    
    def _set(self, key: str, value: Any, ttl: int) -> Any:
        """Set cache value.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            Cached value
        """
        self._cache[key] = {
            "value": value,
            "expires": time.time() + ttl
        }
        return value
    
    def _get(self, key: str) -> Any:
        """Get cache value.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if key not in self._cache:
            return None
        
        item = self._cache[key]
        if time.time() > item["expires"]:
            del self._cache[key]
            return None
        
        return item["value"]


class RetryDecorator:
    """Decorator for retry logic with exponential backoff."""
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0):
        """Initialize retry decorator.
        
        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Base delay between retries in seconds
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
    
    def __call__(self, func):
        """Apply retry decorator to function.
        
        Args:
            func: Function to decorate
            
        Returns:
            Decorated function
        """
        @wraps(func)
        @retry(
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_exponential(multiplier=self.base_delay),
            reraise=True
        )
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Timeout in seconds before attempting to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful execution."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class ServiceLocator(Singleton):
    """Service locator pattern for dependency injection."""
    
    def __init__(self):
        """Initialize service locator."""
        self._services: Dict[str, Any] = {}
    
    def register(self, name: str, service: Any) -> None:
        """Register a service.
        
        Args:
            name: Service name
            service: Service instance
        """
        self._services[name] = service
    
    def get(self, name: str) -> Any:
        """Get a service by name.
        
        Args:
            name: Service name
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service not found
        """
        if name not in self._services:
            raise KeyError(f"Service '{name}' not found")
        return self._services[name]
    
    def has(self, name: str) -> bool:
        """Check if service exists.
        
        Args:
            name: Service name
            
        Returns:
            True if service exists, False otherwise
        """
        return name in self._services 