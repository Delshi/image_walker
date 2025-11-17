import importlib
from typing import Dict, List, Type

from .auto_loader import PluginAutoLoader
from .interface import BaseFilterPlugin


class PluginRegistry:
    """Registry for plugin management with auto-loading capability.

    Attributes:
        _plugins: Dictionary mapping plugin names to plugin classes.
        _auto_loaded: Flag indicating if auto-loading has been performed.
    """

    _plugins: Dict[str, Type[BaseFilterPlugin]] = {}
    _auto_loaded = False

    @classmethod
    def auto_load_plugins(cls):
        """Automatically loads all plugins from standard directories."""
        if cls._auto_loaded:
            return

        print("Auto-loading plugins...")

        # Загружаем плагины из стандартной папки
        plugins_package = "imagewalker.plugins.custom_filters"
        loaded = PluginAutoLoader.load_plugins_from_package(plugins_package)

        print(f"Auto-loaded {len(loaded)} plugins: {loaded}")
        cls._auto_loaded = True

    @classmethod
    def register(cls, name: str = None):
        """Decorator for registering plugin classes.

        Args:
            name: Optional custom name for the plugin.

        Returns:
            Decorator function.
        """

        def decorator(plugin_class: Type[BaseFilterPlugin]):
            # Проверяем, что это действительно класс плагина
            if not isinstance(plugin_class, type) or not issubclass(
                plugin_class, BaseFilterPlugin
            ):
                print(
                    f" \033[31m Warning: {plugin_class} is not a valid plugin class \033[0m "
                )
                return plugin_class

            plugin_name = name or getattr(
                plugin_class, "plugin_name", plugin_class.__name__.lower()
            )
            cls._plugins[plugin_name] = plugin_class
            print(f"Registered plugin: {plugin_name} ({plugin_class.__name__})")
            return plugin_class

        return decorator

    @classmethod
    def get_plugin(cls, name: str) -> Type[BaseFilterPlugin]:
        """Retrieves plugin class by name.

        Args:
            name: Name of the plugin to retrieve.

        Returns:
            Plugin class if found, None otherwise.
        """
        # Автозагружаем плагины при первом обращении
        if not cls._auto_loaded:
            cls.auto_load_plugins()

        return cls._plugins.get(name)

    @classmethod
    def get_available_plugins(cls) -> List[str]:
        """Returns list of all registered plugin names.

        Returns:
            List of available plugin names.
        """
        # Автозагружаем плагины при первом обращении
        if not cls._auto_loaded:
            cls.auto_load_plugins()

        return list(cls._plugins.keys())

    @classmethod
    def create_plugin_instance(cls, name: str):
        """Creates an instance of a plugin.

        Args:
            name: Name of the plugin to instantiate.

        Returns:
            Plugin instance if successful, None otherwise.
        """
        plugin_class = cls.get_plugin(name)
        if plugin_class:
            try:
                instance = plugin_class()
                return instance
            except Exception as e:
                print(f"\033[31m Error creating plugin instance {name}: {e} \033[0m ")
        return None

    @classmethod
    def manually_load_plugin(cls, module_path: str):
        """Manually loads a plugin from a specific module path.

        Args:
            module_path: File path to the plugin module.
        """
        try:
            spec = importlib.util.spec_from_file_location("plugin_module", module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"Manually loaded plugin from: {module_path}")
        except Exception as e:
            print(
                f"\033[31m Failed to manually load plugin {module_path}: {e} \033[0m "
            )

    @classmethod
    def clear_registry(cls):
        """Clears the plugin registry (primarily for testing)."""
        cls._plugins.clear()
        cls._auto_loaded = False
