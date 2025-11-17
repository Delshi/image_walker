import importlib
import sys
from pathlib import Path


class PluginAutoLoader:
    """Automatically loads plugins from specified directories and packages."""

    @classmethod
    def load_plugins_from_directory(cls, directory_path: str | Path):
        """Loads all plugins from a filesystem directory.

        Args:
            directory_path: Path to directory containing plugins.

        Returns:
            List of loaded plugin module names.
        """
        directory = Path(directory_path)

        if not directory.exists():
            print(f"Plugin directory not found: {directory}")
            return

        print(f"Scanning for plugins in: {directory}")

        # Добавляем директорию в sys.path для импорта
        if str(directory.parent) not in sys.path:
            sys.path.insert(0, str(directory.parent))

        loaded_plugins = []

        for file_path in directory.glob("*.py"):
            if file_path.name.startswith("_"):
                continue

            module_name = file_path.stem
            package_name = directory.name

            try:
                full_module_name = f"{package_name}.{module_name}"
                module = importlib.import_module(full_module_name)
                loaded_plugins.append(module_name)
                print(f"Loaded plugin: {module_name}")

            except Exception as e:
                print(f"\t \033[31m Failed to load {module_name}: {e} \033[0m")

        return loaded_plugins

    @classmethod
    def load_plugins_from_package(cls, package_name: str):
        """Loads all plugins from a Python package.

        Args:
            package_name: Name of Python package containing plugins.

        Returns:
            List of loaded plugin module names.
        """
        try:
            package = importlib.import_module(package_name)
            package_path = Path(package.__file__).parent

            return cls.load_plugins_from_directory(package_path)

        except ImportError as e:
            print(f"\t \033[31m Failed to import package {package_name}: {e} \033[0m")
            return []
