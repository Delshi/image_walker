import os
from typing import List

from imagewalker.domain.file_system_domain import File
from imagewalker.repository.walker_repo_interface import IWalkerRepo


class FileOperationsService:
    """Service for file system operations related to sorting."""

    def __init__(self, repo: IWalkerRepo):
        """Initializes the file operations service.

        Args:
            repo: Repository for file system operations.
        """
        self.repo = repo

    def copy_file_to_category_structure(
        self, file: File, categories: List[str], target_root: str
    ) -> str:
        """Copies file to target structure based on categories.

        Args:
            file: File to be copied.
            categories: List of category names for directory structure.
            target_root: Root target directory.

        Returns:
            Full path to the copied file.
        """
        # Составляем абсолютный путь из категорий
        target_path = self._build_category_path(target_root, categories, file.name)

        self.repo.copy_file(file.path, target_path)

        return target_path

    def _build_category_path(
        self, target_root: str, categories: List[str], filename: str
    ) -> str:
        """Builds target path based on categories.

        Args:
            target_root: Root target directory.
            categories: List of category names.
            filename: Name of the file.

        Returns:
            Full target path for the file.
        """
        current_path = target_root

        for category in categories:
            # Очищаем имя категории от недопустимых символов
            clean_category = self._clean_category_name(category)
            current_path = os.path.join(current_path, clean_category)

        self.repo.create_directories(current_path)

        return os.path.join(current_path, filename)

    def _clean_category_name(self, category: str) -> str:
        """Cleans and validates category name for filesystem use.

        Args:
            category: Original category name.

        Returns:
            Cleaned category name safe for filesystem.
        """
        if not category or not isinstance(category, str):
            return "unknown"

        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            category = category.replace(char, "_")

        category = category.strip()
        if len(category) > 255:
            category = category[:255]

        return category
