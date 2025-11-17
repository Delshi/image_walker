from abc import ABC, abstractmethod
from typing import Dict, Generic, List, TypeVar

from imagewalker.domain.file_system_domain import File

T = TypeVar("T")  # Тип файла
M = TypeVar("M")  # Тип метаданных


class Filter(ABC, Generic[T]):
    """Abstract base class for file filters.

    Filters categorize files into groups for organization.
    """

    @abstractmethod
    def get_category(self, file: "File[T]") -> str:
        """Returns the category name for a given file.

        Args:
            file: File to categorize.

        Returns:
            Category name as string.
        """
        pass

    @abstractmethod
    def get_order(self) -> int:
        """Returns the application order priority.

        Returns:
            Integer representing filter application order.
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Returns the filter name.

        Returns:
            Filter name as string.
        """
        pass

    def is_applicable(self, file: "File[T]") -> bool:
        """Determines if filter is applicable to a file.

        Args:
            file: File to check applicability for.

        Returns:
            True if filter can be applied, False otherwise.
        """
        return True

    def get_fallback_category(self) -> str:
        """Returns fallback category for inapplicable files.

        Returns:
            Fallback category name.
        """
        return f"no_{self.get_name()}"


class CompositeFilter(Filter):
    """Combines multiple filters into a sequential filtering pipeline.

    Attributes:
        filters: List of filters sorted by application order.
    """

    def __init__(self, filters: List[Filter]):
        self.filters = sorted(filters, key=lambda f: f.get_order())

    def get_category(self, file: "File") -> List[str]:
        """Applies all filters sequentially and returns category path.

        Args:
            file: File to process through filter pipeline.

        Returns:
            List of category names representing the full path.
        """
        categories = []
        for filter_obj in self.filters:
            try:
                if filter_obj.is_applicable(file):
                    category = filter_obj.get_category(file)
                else:
                    category = filter_obj.get_fallback_category()

                if category is None:
                    category = "unknown"
                categories.append(str(category))

            except Exception as e:
                print(f"Error in filter {filter_obj.get_name()}: {e}")
                categories.append("error")
        return categories

    def get_order(self) -> int:
        return 0

    def get_name(self) -> str:
        return "composite"

    def get_applicable_filters_info(self, file: "File") -> Dict[str, bool]:
        """Returns applicability information for all filters.

        Args:
            file: File to check filter applicability for.

        Returns:
            Dictionary mapping filter names to applicability status.
        """
        return {
            filter_obj.get_name(): filter_obj.is_applicable(file)
            for filter_obj in self.filters
        }
