from typing import Dict, Any, List
from imagewalker.domain.file_system_domain import File
from imagewalker.filters.filters import CompositeFilter, Filter


class StatsService:
    """Service for tracking and reporting sorting statistics."""

    @staticmethod
    def initialize_stats(filters: List[Filter]) -> Dict[str, Any]:
        """Initializes statistics dictionary.

        Args:
            filters: List of filters to track.

        Returns:
            Initialized statistics dictionary.
        """
        return {
            "total_files": 0,
            "files_by_filter": {filter_obj.get_name(): 0 for filter_obj in filters},
            "skipped_files": 0,
        }

    @staticmethod
    def update_file_stats(
        stats: Dict[str, Any], composite_filter: CompositeFilter, file: File
    ) -> None:
        """Updates statistics for a processed file.

        Args:
            stats: Statistics dictionary to update.
            composite_filter: Composite filter for applicability check.
            file: Processed file.
        """
        stats["total_files"] += 1

        # Обновляем счетчик применений фильтра
        filter_info = composite_filter.get_applicable_filters_info(file)
        for filter_name, applicable in filter_info.items():
            if applicable:
                stats["files_by_filter"][filter_name] += 1

    @staticmethod
    def print_sorting_stats(stats: Dict[str, Any]) -> None:
        """Prints sorting statistics to console.

        Args:
            stats: Statistics dictionary to print.
        """
        print("\nRESULT:")
        print(f"   Total files processed: {stats['total_files']}")
        print(f"   Skipped files: {stats['skipped_files']}")

        if stats["total_files"] > 0:
            print("\n   Files applicable to each filter:")
            for filter_name, count in stats["files_by_filter"].items():
                percentage = (count / stats["total_files"]) * 100
                print(f"     {filter_name}: {count} files ({percentage:.1f}%)")
