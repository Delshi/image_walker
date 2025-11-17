import importlib
import inspect
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from imagewalker.plugins.interface import BaseFilterPlugin


class PluginConnector:
    """Handles automatic discovery and loading of plugins from various sources.

    Attributes:
        plugin_packages: List of packages to search for plugins.
        _discovered_plugins: Cache of discovered plugin classes.
        _plugin_instances: Cache of instantiated plugins.
    """

    def __init__(self, plugin_packages: List[str] = None):
        self.plugin_packages = plugin_packages or []
        self._discovered_plugins: Dict[str, Type[BaseFilterPlugin]] = {}
        self._plugin_instances: Dict[str, BaseFilterPlugin] = {}

    def discover_plugins(
        self, search_paths: List[str] = None
    ) -> Dict[str, Type[BaseFilterPlugin]]:
        """Discovers plugins in specified search paths.

        Args:
            search_paths: Optional list of paths to search.

        Returns:
            Dictionary mapping plugin names to plugin classes.
        """
        discovered = {}

        # Стандартные пути поиска
        search_paths = search_paths or []
        search_paths.extend(self.plugin_packages)

        print(f"Searching for plugins in paths: {search_paths}")

        # Ищем в текущей директории плагинов
        plugins_dir = Path(__file__).parent / "custom_filters"
        if plugins_dir.exists():
            search_paths.append(str(plugins_dir))
            print(f"Added plugins directory: {plugins_dir}")

        for search_path in search_paths:
            print(f"Searching in: {search_path}")
            path_plugins = self._discover_in_path(search_path)
            discovered.update(path_plugins)
            if path_plugins:
                print(f"Found {len(path_plugins)} plugins in {search_path}")

        self._discovered_plugins = discovered
        print(f"Total discovered plugins: {list(discovered.keys())}")
        return discovered

    def _discover_in_path(self, search_path: str) -> Dict[str, Type[BaseFilterPlugin]]:
        """Discovers plugins in a specific path.

        Args:
            search_path: Path to search for plugins.

        Returns:
            Dictionary of discovered plugins from this path.
        """
        plugins = {}

        try:
            # Если путь существует как директория
            path_obj = Path(search_path)
            if path_obj.exists() and path_obj.is_dir():
                plugins.update(self._discover_in_directory(search_path))
            else:
                # Пытаемся обработать как Python пакет
                plugins.update(self._discover_in_package(search_path))

        except Exception as e:
            print(f" \033[31m Error discovering plugins in {search_path}: {e} \033[0m ")
            import traceback

            traceback.print_exc()

        return plugins

    def _discover_in_package(
        self, package_name: str
    ) -> Dict[str, Type[BaseFilterPlugin]]:
        """Discovers plugins in a Python package.

        Args:
            package_name: Name of the Python package to search.

        Returns:
            Dictionary of discovered plugins from this package.
        """
        plugins = {}

        try:
            print(f" \033[31m Importing package: {package_name} \033[0m ")
            package = importlib.import_module(package_name)

            # Получаем путь пакета
            if hasattr(package, "__path__"):
                package_path = package.__path__[0]
                print(f"  Package path: {package_path}")

                # Сканируем директорию пакета
                plugins.update(self._scan_directory(package_path))
            else:
                print(f" \033[31m Package {package_name} has no __path__ \033[0m ")

        except ImportError as e:
            print(f" \033[31m Error importing package {package_name}: {e} \033[0m ")
        except Exception as e:
            print(
                f" \033[31m Unexpected error with package {package_name}: {e} \033[0m "
            )

        return plugins

    def _discover_in_directory(
        self, directory_path: str
    ) -> Dict[str, Type[BaseFilterPlugin]]:
        """Discovers plugins in a filesystem directory.

        Args:
            directory_path: Directory path to search.

        Returns:
            Dictionary of discovered plugins from this directory.
        """
        plugins = {}
        directory = Path(directory_path)

        if not directory.exists():
            print(f" \033[31m Directory does not exist: {directory_path} \033[0m ")
            return plugins

        print(f"  Scanning directory: {directory_path}")
        plugins.update(self._scan_directory(directory_path))

        return plugins

    def _scan_directory(self, directory_path: str) -> Dict[str, Type[BaseFilterPlugin]]:
        """Scans a directory for plugin modules.

        Args:
            directory_path: Directory to scan.

        Returns:
            Dictionary of discovered plugins.
        """
        plugins = {}
        directory = Path(directory_path)

        # Добавляем директорию в sys.path для импорта
        original_sys_path = sys.path.copy()
        if str(directory.parent) not in sys.path:
            sys.path.insert(0, str(directory.parent))

        try:
            for file_path in directory.glob("*.py"):
                if file_path.name.startswith("_"):
                    continue

                module_name = file_path.stem
                package_path = directory.parent.name
                full_module_name = f"{package_path}.{directory.name}.{module_name}"

                print(f"    Loading module: {full_module_name} from {file_path}")

                try:
                    module = importlib.import_module(full_module_name)
                    module_plugins = self._find_plugins_in_module(module)
                    plugins.update(module_plugins)

                    if module_plugins:
                        print(
                            f"    Found {len(module_plugins)} plugins in {module_name}"
                        )

                except Exception as e:
                    print(
                        f"    \033[31m Error loading module {module_name}: {e} \033[0m "
                    )
                    # Пробуем загрузить напрямую из файла
                    try:
                        spec = importlib.util.spec_from_file_location(
                            module_name, file_path
                        )
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            module_plugins = self._find_plugins_in_module(module)
                            plugins.update(module_plugins)

                            if module_plugins:
                                print(
                                    f"    Found {len(module_plugins)} plugins in {file_path.name} (direct load)"
                                )
                    except Exception as e2:
                        print(
                            f"    \033[31m Error loading plugin from {file_path}: {e2} \033[0m "
                        )

        except Exception as e:
            print(f"   \033[31m Error scanning directory {directory_path}: {e} \033[0m")
        finally:
            # Восстанавливаем sys.path
            sys.path = original_sys_path

        return plugins

    def _find_plugins_in_module(self, module) -> Dict[str, Type[BaseFilterPlugin]]:
        """Finds plugin classes in a loaded module.

        Args:
            module: Python module to inspect.

        Returns:
            Dictionary of plugin classes found in module.
        """
        plugins = {}

        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, BaseFilterPlugin)
                and obj != BaseFilterPlugin
            ):

                plugin_name = getattr(obj, "plugin_name", name.lower())
                plugins[plugin_name] = obj
                print(f"      Discovered plugin: {plugin_name}")

        return plugins

    def get_available_plugins(self) -> List[str]:
        """Returns list of available plugin names.

        Returns:
            List of discovered plugin names.
        """
        return list(self._discovered_plugins.keys())

    def create_plugin_instance(self, plugin_name: str) -> Optional[BaseFilterPlugin]:
        """Creates an instance of a discovered plugin.

        Args:
            plugin_name: Name of the plugin to instantiate.

        Returns:
            Plugin instance if found, None otherwise.
        """
        if plugin_name not in self._discovered_plugins:
            print(
                f" \033[31m Plugin '{plugin_name}' not found. \033[0m Available: {list(self._discovered_plugins.keys())}"
            )
            return None

        if plugin_name not in self._plugin_instances:
            plugin_class = self._discovered_plugins[plugin_name]
            self._plugin_instances[plugin_name] = plugin_class()

        return self._plugin_instances[plugin_name]

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Returns information about a specific plugin.

        Args:
            plugin_name: Name of the plugin.

        Returns:
            Plugin information dictionary if found, None otherwise.
        """
        plugin_class = self._discovered_plugins.get(plugin_name)
        if plugin_class:
            return plugin_class.get_plugin_info()
        return None
