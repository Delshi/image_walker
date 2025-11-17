# plugins/custom_filters/custom_size_plugin.py
from dataclasses import dataclass
from typing import Dict, Any
from imagewalker.plugins.interface import (
    BaseFilterPlugin,
    PluginConfig,
    template_plugin,
)
from imagewalker.plugins.registry import PluginRegistry
from imagewalker.filters.implementation import ByteSizeStepFilter


@dataclass
class CustomSizeConfig(PluginConfig):
    """Configuration for custom size grouping plugin.

    Attributes:
        unit: Size unit ('KB', 'MB', 'GB').
        custom_step: Step size in the specified unit.
    """

    unit: str = "MB"
    custom_step: float = 5.0


@template_plugin
@PluginRegistry.register("custom_size")
class CustomSizePlugin(BaseFilterPlugin):
    """Plugin for custom file size grouping with configurable units."""

    def create_filter(self, config: Dict[str, Any]):
        unit = config.get("unit", "MB")
        step = config.get("custom_step", 5.0)

        # Конвертируем в байты
        unit_multipliers = {"KB": 1024, "MB": 1024 * 1024, "GB": 1024 * 1024 * 1024}

        step_bytes = int(step * unit_multipliers.get(unit, 1))

        return ByteSizeStepFilter(order=config.get("order", 0), step_bytes=step_bytes)

    @classmethod
    def get_config_class(cls):
        return CustomSizeConfig
