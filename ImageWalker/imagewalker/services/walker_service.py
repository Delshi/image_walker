import os
from pathlib import Path
from typing import Any, Dict, List

from imagewalker.domain.file_system_domain import Directory, File
from imagewalker.filters.filters import CompositeFilter, Filter
from imagewalker.filters.registry import FilterRegistry
from imagewalker.repository.walker_repo_interface import IWalkerRepo
from imagewalker.services.file_operations_service import FileOperationsService
from imagewalker.services.stats_service import StatsService


class WalkerService:
    """Main service orchestrating file sorting operations."""

    def __init__(
        self,
        repo: IWalkerRepo,
        source_path: str,
        allowed_ext: List[str] | None = None,
        filter_registry: FilterRegistry | None = None,
        file_operations: FileOperationsService = None,
        stats_service: StatsService = None,
    ):
        """Initializes the WalkerService.

        Args:
            repo: File system repository.
            source_path: Source directory path.
            allowed_ext: List of allowed file extensions.
            filter_registry: Registry for filter management.
            file_operations: Service for file operations.
            stats_service: Service for statistics tracking.
        """
        self.repo = repo
        self.source_path = source_path
        self.allowed_ext = allowed_ext or self._get_default_extensions()
        self.filter_registry = filter_registry or FilterRegistry()
        self.file_operations = file_operations or FileOperationsService(repo)
        self.stats_service = stats_service or StatsService()

    def _get_default_extensions(self) -> List[str]:
        """Provides default list of allowed file extensions.

        Returns:
            List of default file extensions.
        """
        return [
            "JPEG",
            "PNG",
            "GIF",
            "WEBP",
            "TIFF",
            "BMP",
            "ICO",
            "SVG",
            "RAW",
            "EPS",
            "MP4",
            "AVI",
            "MKV",
            "MOV",
            "MP3",
            "WAV",
        ]

    def get_available_filters_with_info(self) -> Dict[str, Any]:
        """Returns information about all available filters.

        Returns:
            Dictionary mapping filter names to their information.
        """
        filters_info = {}
        for filter_name in self.filter_registry.get_available_filters():
            info = self.filter_registry.get_filter_info(filter_name)
            if info:
                filters_info[filter_name] = info
        return filters_info

    def sort_by(
        self, filters_config: List[Dict[str, Any]], dest: str | None = None
    ) -> Directory:
        """Sorts files using specified filters and configuration.

        Args:
            filters_config: List of filter configurations.
            dest: Optional destination directory path.

        Returns:
            Directory tree representing the sorted file structure.

        Raises:
            Exception: If any error occurs during sorting.
        """
        try:
            # Фильтры из конфигурации
            filters = self._create_filters(filters_config)

            source_tree = self.repo.get_tree(
                path=self.source_path, allowed_ext=self.allowed_ext
            )
            print(f"Found source tree with {self._count_files(source_tree)} files")

            target_dir = self._create_target_directory(dest)
            print(f"Target directory: {target_dir}")

            result_tree = self._sort_files(source_tree, filters, target_dir)
            print("Sorting completed successfully")

            return result_tree

        except Exception as e:
            print(f"Error in sort_by: {e}")
            raise

    def _create_filters(self, filters_config: List[Dict[str, Any]]) -> List[Filter]:
        """Creates filter instances from configuration.

        Args:
            filters_config: List of filter configurations.

        Returns:
            List of instantiated filter objects.
        """
        filters = []
        print(f"Processing filters config: {filters_config}")

        for config in filters_config:
            config_copy = config.copy()
            filter_name = config_copy.pop("name")

            filter_obj = self.filter_registry.create_filter(filter_name, config_copy)
            print(
                f"Created filter: {filter_obj.get_name()} (order: {filter_obj.get_order()})"
            )
            filters.append(filter_obj)

        print(f"Created {len(filters)} filters: {[f.get_name() for f in filters]}")
        return filters

    def _create_target_directory(self, dest: str | None) -> str:
        """Creates target directory for sorted files.

        Args:
            dest: Optional destination path.

        Returns:
            Path to created target directory.
        """
        if dest:
            return self.repo.create_new_entry(dest=dest)
        else:
            # Создаем директорию около исходной, если не передана целевая
            source_path = Path(self.source_path)
            target_dir_name = f"{source_path.name}_sorted"
            target_dir = source_path.parent / target_dir_name
            return self.repo.create_new_entry(dest=str(target_dir))

    def _sort_files(
        self, source_tree: Directory, filters: List[Filter], target_root: str
    ) -> Directory:
        """Orchestrates file sorting process.

        Args:
            source_tree: Source directory tree.
            filters: List of filters to apply.
            target_root: Root target directory.

        Returns:
            Directory tree representing sorted structure.
        """
        composite_filter = CompositeFilter(filters)
        result_root = Directory("sorted", target_root)
        stats = self.stats_service.initialize_stats(filters)

        def _process_directory(source_dir: Directory, current_result_dir: Directory):
            """Processes directory and its contents recursively."""

            for file in source_dir.files:
                self._process_single_file(file, composite_filter, stats, target_root)

            # Рекурсивно подпапки обрабатываем
            for subdir in source_dir.subdirectories:
                if self._has_allowed_files(subdir):
                    self._process_subdirectory(
                        subdir, current_result_dir, _process_directory
                    )

        # Старт обработки с исходной
        _process_directory(source_tree, result_root)

        self.stats_service.print_sorting_stats(stats)

        return result_root

    def _process_single_file(
        self,
        file: File,
        composite_filter: CompositeFilter,
        stats: Dict[str, Any],
        target_root: str,
    ) -> None:
        """Processes a single file through the sorting pipeline.

        Args:
            file: File to process.
            composite_filter: Composite filter for categorization.
            stats: Statistics dictionary to update.
            target_root: Root target directory.
        """
        try:
            categories = composite_filter.get_category(file)

            # Сохраняем категорию файла
            self.file_operations.copy_file_to_category_structure(
                file, categories, target_root
            )

            self.stats_service.update_file_stats(stats, composite_filter, file)

        except Exception as e:
            print(f"Error processing file {file.name}: {e}")
            stats["skipped_files"] += 1

    def _process_subdirectory(
        self,
        source_subdir: Directory,
        current_result_dir: Directory,
        process_func: callable,
    ) -> None:
        """Processes a subdirectory recursively.

        Args:
            source_subdir: Source subdirectory to process.
            current_result_dir: Current result directory.
            process_func: Processing function to call recursively.
        """
        try:
            result_subdir_path = os.path.join(
                current_result_dir.path, source_subdir.name
            )
            result_subdir = Directory(source_subdir.name, result_subdir_path)
            current_result_dir.add_subdirectory(result_subdir)
            process_func(source_subdir, result_subdir)
        except Exception as e:
            print(f"Error processing subdirectory {source_subdir.name}: {e}")

    def _has_allowed_files(self, directory: Directory) -> bool:
        """Checks if directory contains files with allowed extensions.

        Args:
            directory: Directory to check.

        Returns:
            True if directory contains allowed files, False otherwise.
        """
        if directory.files:
            return True

        for subdir in directory.subdirectories:
            if self._has_allowed_files(subdir):
                return True

        return False

    def _count_files(self, directory: Directory) -> int:
        """Recursively counts files in directory tree.

        Args:
            directory: Root directory to count from.

        Returns:
            Total number of files in directory tree.
        """
        count = len(directory.files)
        for subdir in directory.subdirectories:
            count += self._count_files(subdir)
        return count
