from dataclasses import dataclass
from typing import Dict, Any
import datetime
import os
from imagewalker.domain.file_system_domain import File
from imagewalker.plugins.interface import (
    BaseFilterPlugin,
    PluginConfig,
    template_plugin,
)
from imagewalker.plugins.registry import PluginRegistry
from imagewalker.filters.filters import Filter


@dataclass
class DateRangeConfig(PluginConfig):
    """Configuration for date range grouping plugin.

    Attributes:
        range_days: Number of days per range group.
    """

    range_days: int = 30


@template_plugin
@PluginRegistry.register("date_range")
class DateRangePlugin(BaseFilterPlugin):
    """Plugin for grouping files by date ranges."""

    def create_filter(self, config: Dict[str, Any]):
        return DateRangeFilter(
            order=config.get("order", 0), range_days=config.get("range_days", 30)
        )

    @classmethod
    def get_config_class(cls):
        return DateRangeConfig


class DateRangeFilter(Filter):
    """Filter that categorizes files by modification date ranges."""

    def __init__(self, range_days: int = 30, order: int = 0):
        self.range_days = range_days
        self._order = order

    def get_category(self, file: "File") -> str:
        try:
            stat = os.stat(file.path)
            modified_time = stat.st_mtime
            modified_date = datetime.datetime.fromtimestamp(modified_time)

            # Группируем по диапазонам дней
            days_ago = (datetime.datetime.now() - modified_date).days
            range_num = days_ago // self.range_days
            start_days = range_num * self.range_days
            end_days = start_days + self.range_days

            if range_num == 0:
                return f"last_{end_days}_days"
            else:
                return f"{start_days}-{end_days}_days_ago"

        except Exception:
            return "unknown_date"

    def get_order(self) -> int:
        return self._order

    def get_name(self) -> str:
        return "date_range"

    def is_applicable(self, file: "File") -> bool:
        return True
