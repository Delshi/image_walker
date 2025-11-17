from abc import ABC, abstractmethod
from typing import List

from imagewalker.domain.file_system_domain import Directory


class IWalkerRepo(ABC):
    """Interface for file system repository operations."""

    @staticmethod
    @abstractmethod
    def get_tree(path: str, allowed_ext: List[str]) -> Directory:
        """Builds a file system tree structure.

        Args:
            path: Root path to build tree from.
            allowed_ext: List of allowed file extensions.

        Returns:
            Directory object representing the file system tree.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def create_new_entry(dest: str) -> str:
        """Creates a new directory entry.

        Args:
            dest: Destination directory path.

        Returns:
            Path to created directory.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def copy_file(source_path: str, target_path: str) -> None:
        """Copies a file from source to target location.

        Args:
            source_path: Path to source file.
            target_path: Path to target location.

        Raises:
            Exception: If copying fails.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def create_directories(path: str) -> None:
        """Creates directories recursively.

        Args:
            path: Path where directories should be created.
        """
        raise NotImplementedError
