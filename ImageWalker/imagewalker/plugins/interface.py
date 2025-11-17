from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Dict, Type


def template_plugin(func):
    """Decorator that ensures plugin classes are dataclasses.

    Args:
        cls: Class to decorate as plugin.

    Returns:
        The decorated class.

    Raises:
        TypeError: If class is not a dataclass.
    """

    @wraps(func)
    def wrapper(cls):
        if not hasattr(cls, "__dataclass_fields__"):
            raise TypeError(f"{cls.__name__} must be a dataclass.")

        setattr(cls, "plugin_data", field(default_factory=dict))
        return func(cls)

    return wrapper


@dataclass
class PluginConfig:
    """Base configuration class for plugins.

    Attributes:
        name: Plugin name.
        version: Plugin version string.
        description: Plugin description.
        enabled: Whether plugin is active.
        plugin_data: Additional plugin-specific data.
    """

    name: str
    version: str = "1.0.0"
    description: str = ""
    enabled: bool = True
    plugin_data: Dict[str, Any] = field(default_factory=dict)


class BaseFilterPlugin(ABC):
    """Abstract base class for filter plugins."""

    @abstractmethod
    def create_filter(self, config: Dict[str, Any]):
        """Creates a filter instance from plugin configuration.

        Args:
            config: Plugin configuration parameters.

        Returns:
            Instantiated filter object.
        """
        pass

    @classmethod
    @abstractmethod
    def get_config_class(cls) -> Type[PluginConfig]:
        """Returns the configuration class for this plugin.

        Returns:
            PluginConfig subclass specific to this plugin.
        """
        pass

    @classmethod
    def get_plugin_info(cls) -> Dict[str, Any]:
        """Returns plugin metadata information.

        Returns:
            Dictionary containing plugin name, config fields, and description.
        """
        config_class = cls.get_config_class()
        return {
            "name": cls.__name__,
            "config_fields": list(config_class.__dataclass_fields__.keys()),
            "description": getattr(cls, "__doc__", "").strip() if cls.__doc__ else "",
        }
