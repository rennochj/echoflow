"""Dependency injection container for EchoFlow."""

from typing import Any, Callable, Optional, TypeVar

from ..exceptions.base import ConfigurationError

T = TypeVar("T")


class Container:
    """Simple dependency injection container."""

    def __init__(self) -> None:
        """Initialize the container."""
        self._services: dict[str, Any] = {}
        self._factories: dict[str, Callable[[], Any]] = {}
        self._singletons: dict[str, Any] = {}

    def register_instance(self, service_type: type[T], instance: T) -> None:
        """Register a service instance.

        Args:
            service_type: The service type/interface
            instance: The service instance
        """
        key = self._get_key(service_type)
        self._services[key] = instance

    def register_factory(self, service_type: type[T], factory: Callable[[], T]) -> None:
        """Register a service factory function.

        Args:
            service_type: The service type/interface
            factory: Factory function that creates the service
        """
        key = self._get_key(service_type)
        self._factories[key] = factory

    def register_singleton(self, service_type: type[T], factory: Callable[[], T]) -> None:
        """Register a singleton service factory.

        Args:
            service_type: The service type/interface
            factory: Factory function that creates the service (called once)
        """
        key = self._get_key(service_type)
        self._factories[key] = factory
        # Mark as singleton by adding to singletons dict (but don't create yet)
        self._singletons[key] = None

    def get(self, service_type: type[T]) -> T:
        """Get a service instance.

        Args:
            service_type: The service type to resolve

        Returns:
            Service instance

        Raises:
            ConfigurationError: If service is not registered
        """
        key = self._get_key(service_type)

        # Check for direct instance
        if key in self._services:
            return self._services[key]

        # Check for singleton
        if key in self._singletons:
            if self._singletons[key] is None:
                # Create singleton instance
                if key not in self._factories:
                    raise ConfigurationError(f"No factory registered for {service_type}")
                self._singletons[key] = self._factories[key]()
            return self._singletons[key]

        # Check for factory
        if key in self._factories:
            return self._factories[key]()

        raise ConfigurationError(f"Service not registered: {service_type}")

    def try_get(self, service_type: type[T]) -> Optional[T]:
        """Try to get a service instance.

        Args:
            service_type: The service type to resolve

        Returns:
            Service instance or None if not found
        """
        try:
            return self.get(service_type)
        except ConfigurationError:
            return None

    def is_registered(self, service_type: type[T]) -> bool:
        """Check if a service is registered.

        Args:
            service_type: The service type to check

        Returns:
            True if the service is registered
        """
        key = self._get_key(service_type)
        return key in self._services or key in self._factories

    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()

    def _get_key(self, service_type: type) -> str:
        """Get the key for a service type.

        Args:
            service_type: The service type

        Returns:
            String key for the service
        """
        return f"{service_type.__module__}.{service_type.__qualname__}"


# Global container instance
container = Container()
