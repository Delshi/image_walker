from typing import Dict, Any, Callable, List, Optional
from imagewalker.plugins.registry import PluginRegistry
from imagewalker.plugins.interface import BaseFilterPlugin


class FilterRegistry:
    """Registry for managing both built-in and plugin filters.

    Attributes:
        _filters: Dictionary mapping filter names to factory functions.
    """

    def __init__(self):
        self._filters: Dict[str, Callable] = {}

        self._register_builtin_filters()

        available_plugins = PluginRegistry.get_available_plugins()
        print(f"Available plugins: {available_plugins}")

    def _register_builtin_filters(self):
        """Registers all built-in filter implementations."""
        from .implementation import (
            ExtensionFilter,
            ByteSizeStepFilter,
            DurationFilter,
            ResolutionFilter,
            DateCreatedFilter,
        )

        builtin_filters = {
            "extension": ExtensionFilter,
            "byte_size": ByteSizeStepFilter,
            "duration": DurationFilter,
            "resolution": ResolutionFilter,
            "date_created": DateCreatedFilter,
        }

        for name, filter_class in builtin_filters.items():
            self.register_filter(name, self._create_filter_factory(filter_class))

        print(f"Registered {len(builtin_filters)} built-in filters")

    def _create_filter_factory(self, filter_class):
        """Creates a filter factory function.

        Args:
            filter_class: Filter class to create factory for.

        Returns:
            Factory function that instantiates the filter.
        """

        def factory(**kwargs):
            return filter_class(**kwargs)

        return factory

    def register_filter(self, name: str, filter_factory: Callable):
        """Registers a built-in filter.

        Args:
            name: Filter name for registration.
            filter_factory: Factory function that creates filter instances.
        """
        self._filters[name] = filter_factory

    def create_filter(self, name: str, config: Dict[str, Any]):
        """Creates a filter instance by name with configuration.

        Args:
            name: Name of the filter to create.
            config: Configuration parameters for the filter.

        Returns:
            Instantiated filter object.

        Raises:
            ValueError: If filter name is not found.
        """
        print(f"Creating filter: {name} with config: {config}")

        # Пытаемся создать встроенный фильтр
        if name in self._filters:
            print(f"Using builtin filter: {name}")
            filter_instance = self._filters[name](**config)
            print(f"Created filter instance: {filter_instance.get_name()}")
            return filter_instance

        # Пытаемся создать фильтр через плагин
        print(f"Trying to use plugin: {name}")
        plugin_instance = PluginRegistry.create_plugin_instance(name)
        if plugin_instance:
            print(f"Plugin instance created: {plugin_instance}")
            filter_instance = plugin_instance.create_filter(config)
            print(f"Created plugin filter instance: {filter_instance.get_name()}")
            return filter_instance

        available_filters = self.get_available_filters()
        raise ValueError(f"Filter '{name}' not found. Available: {available_filters}")

    def get_available_filters(self) -> List[str]:
        """Returns list of all available filter names.

        Returns:
            List of built-in and plugin filter names.
        """
        builtin_filters = list(self._filters.keys())
        plugin_filters = PluginRegistry.get_available_plugins()
        return builtin_filters + plugin_filters

    def get_filter_info(self, filter_name: str) -> Optional[Dict[str, Any]]:
        """Returns information about a specific filter.

        Args:
            filter_name: Name of the filter to get info for.

        Returns:
            Dictionary with filter information, or None if not found.
        """
        if filter_name in self._filters:
            return {"type": "builtin", "name": filter_name}

        plugin_class = PluginRegistry.get_plugin(filter_name)
        if plugin_class and hasattr(plugin_class, "get_plugin_info"):
            return plugin_class.get_plugin_info()

        return None
