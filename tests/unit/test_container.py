"""Unit tests for dependency injection container."""

import pytest

from src.echoflow.exceptions.base import ConfigurationError
from src.echoflow.utils.container import Container


class ServiceForTesting:
    """Test service for dependency injection (renamed to avoid pytest collection)."""

    def __init__(self, value: str = "default"):
        self.value = value


class TestContainer:
    """Test Container functionality."""

    def test_register_and_get_instance(self):
        """Test registering and retrieving service instances."""
        container = Container()
        service = ServiceForTesting("test_value")

        container.register_instance(ServiceForTesting, service)
        retrieved = container.get(ServiceForTesting)

        assert retrieved is service
        assert retrieved.value == "test_value"

    def test_register_and_get_factory(self):
        """Test registering and using factory functions."""
        container = Container()

        def create_service() -> ServiceForTesting:
            return ServiceForTesting("factory_value")

        container.register_factory(ServiceForTesting, create_service)
        retrieved = container.get(ServiceForTesting)

        assert isinstance(retrieved, ServiceForTesting)
        assert retrieved.value == "factory_value"

        # Should create new instance each time
        retrieved2 = container.get(ServiceForTesting)
        assert retrieved2 is not retrieved
        assert retrieved2.value == "factory_value"

    def test_register_and_get_singleton(self):
        """Test registering and using singleton services."""
        container = Container()

        def create_service() -> ServiceForTesting:
            return ServiceForTesting("singleton_value")

        container.register_singleton(ServiceForTesting, create_service)
        retrieved = container.get(ServiceForTesting)

        assert isinstance(retrieved, ServiceForTesting)
        assert retrieved.value == "singleton_value"

        # Should return same instance
        retrieved2 = container.get(ServiceForTesting)
        assert retrieved2 is retrieved

    def test_service_not_registered(self):
        """Test error when service is not registered."""
        container = Container()

        with pytest.raises(ConfigurationError, match="Service not registered"):
            container.get(ServiceForTesting)

    def test_try_get_returns_none_for_unregistered(self):
        """Test try_get returns None for unregistered services."""
        container = Container()

        result = container.try_get(ServiceForTesting)
        assert result is None

    def test_try_get_returns_service_when_registered(self):
        """Test try_get returns service when registered."""
        container = Container()
        service = ServiceForTesting("test")
        container.register_instance(ServiceForTesting, service)

        result = container.try_get(ServiceForTesting)
        assert result is service

    def test_is_registered(self):
        """Test is_registered method."""
        container = Container()

        assert not container.is_registered(ServiceForTesting)

        container.register_instance(ServiceForTesting, ServiceForTesting())
        assert container.is_registered(ServiceForTesting)

    def test_clear_container(self):
        """Test clearing all services."""
        container = Container()
        service = ServiceForTesting("test")
        container.register_instance(ServiceForTesting, service)

        assert container.is_registered(ServiceForTesting)

        container.clear()
        assert not container.is_registered(ServiceForTesting)

    def test_factory_error_propagates(self):
        """Test that factory errors are propagated."""
        container = Container()

        def failing_factory() -> ServiceForTesting:
            raise ValueError("Factory failed")

        container.register_factory(ServiceForTesting, failing_factory)

        with pytest.raises(ValueError, match="Factory failed"):
            container.get(ServiceForTesting)
