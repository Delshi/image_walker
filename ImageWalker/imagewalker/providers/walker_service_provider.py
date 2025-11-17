from imagewalker.repository.walker_repo_interface import IWalkerRepo
from imagewalker.services.walker_service import WalkerService
from imagewalker.services.file_operations_service import FileOperationsService
from imagewalker.services.stats_service import StatsService


def get_walker_service(
    walker_repo: IWalkerRepo,
    source_path: str,
    allowed_ext: list[str] | None = None,
) -> WalkerService:
    """Factory function for creating WalkerService instances.

    Args:
        walker_repo: Repository implementation for file system access.
        source_path: Source directory path.
        allowed_ext: Optional list of allowed file extensions.

    Returns:
        Configured WalkerService instance.
    """
    file_operations = FileOperationsService(walker_repo)
    stats_service = StatsService()

    return WalkerService(
        repo=walker_repo(),
        source_path=source_path,
        allowed_ext=allowed_ext,
        file_operations=file_operations,
        stats_service=stats_service,
    )
