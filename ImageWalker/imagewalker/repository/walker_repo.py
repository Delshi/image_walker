import os
from pathlib import Path
from typing import Dict, List
import shutil

from imagewalker.domain.file_system_domain import Directory, FileFactory
from imagewalker.repository.walker_repo_interface import IWalkerRepo


class WalkerRepository(IWalkerRepo):
    """Concrete implementation of file system repository."""

    @staticmethod
    def create_new_entry(dest: str) -> str:
        """Creates a new directory and returns its path.

        Args:
            dest: Destination directory path.

        Returns:
            Path to created directory.

        Raises:
            ValueError: If destination path is empty.
        """
        if not dest:
            raise ValueError("Destination path cannot be empty")

        dest_path = Path(dest)
        dest_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dest_path}")
        return str(dest_path)

    @staticmethod
    def get_tree(path: str, allowed_ext: List[str]) -> Directory:
        """Builds file system tree filtered by allowed extensions.

        Args:
            path: Root directory path.
            allowed_ext: List of allowed file extensions.

        Returns:
            Directory tree containing only files with allowed extensions.
        """
        # Нормализация расширений
        allowed_ext_upper = [
            ext.upper() if ext.startswith(".") else f".{ext.upper()}"
            for ext in allowed_ext
        ]

        root_dir = Directory("root", path)
        dir_cache: Dict[str, Directory] = {path: root_dir}

        for dirpath, dirnames, filenames in os.walk(path):
            current_dir = dir_cache[dirpath]

            for dirname in dirnames:
                dir_full_path = os.path.join(dirpath, dirname)
                new_dir = Directory(dirname, dir_full_path)
                current_dir.add_subdirectory(new_dir)
                dir_cache[dir_full_path] = new_dir

            for filename in filenames:
                file_ext = os.path.splitext(filename)[1].upper()
                if file_ext in allowed_ext_upper:
                    file_full_path = os.path.join(dirpath, filename)
                    file_obj = FileFactory.create_file(file_full_path)
                    current_dir.add_file(file_obj)

        return root_dir

    @staticmethod
    def copy_file(source_path: str, target_path: str) -> None:
        """Copies a file from source to target location.

        Args:
            source_path: Path to source file.
            target_path: Path to target location.

        Raises:
            Exception: If copying fails.
        """
        try:
            Path(target_path).parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(source_path, target_path)
            print(f"Copied: {source_path} -> {target_path}")

        except Exception as e:
            print(f"Error copying file {source_path} to {target_path}: {e}")
            raise

    @staticmethod
    def create_directories(path: str) -> None:
        """Creates directories recursively.

        Args:
            path: Path where directories should be created.
        """
        Path(path).mkdir(parents=True, exist_ok=True)
