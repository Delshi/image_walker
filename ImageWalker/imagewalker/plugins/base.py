from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar

from imagewalker.filters.filters import Filter

T = TypeVar("T")  # Тип файла


class FilterPlugin(ABC, Generic[T]):
    """Базовый класс для плагинов фильтров"""

    @abstractmethod
    def create_filter(self, config: Dict[str, Any]) -> Filter[T]:
        pass
