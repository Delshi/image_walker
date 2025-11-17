import os

from imagewalker.domain.file_system_domain import File
from imagewalker.filters.filters import Filter


class ByteSizeStepFilter(Filter):
    """Filters files by size using configurable byte steps.

    Categories are named in megabytes for readability.
    """

    def __init__(self, step_bytes: int, order: int = 1):
        self.step_bytes = step_bytes
        self._order = order

    def get_category(self, file: "File") -> str:
        try:
            size = file.metadata.size_bytes
            step = self.step_bytes
            lower_bound = (size // step) * step
            upper_bound = lower_bound + step
            return f"{lower_bound/1e6:0.1f}-{upper_bound/1e6:0.1f}_MB"
        except (AttributeError, TypeError):
            return "unknown_size"

    def get_order(self) -> int:
        return self._order

    def get_name(self) -> str:
        return "byte_size"

    def is_applicable(self, file: "File") -> bool:
        try:
            return (
                hasattr(file.metadata, "size_bytes")
                and file.metadata.size_bytes is not None
            )
        except Exception:
            return False


class DurationFilter(Filter):
    """Filters files by duration using configurable time steps.

    Primarily used for audio and video files.
    """

    def __init__(self, step_seconds: float = 60.0, order: int = 2):
        self.step_seconds = step_seconds
        self._order = order

    def get_category(self, file: "File") -> str:
        try:
            if (
                hasattr(file.metadata, "duration")
                and file.metadata.duration is not None
            ):
                duration = file.metadata.duration
                step = self.step_seconds
                lower_bound = int((duration // step) * step)
                upper_bound = lower_bound + step
                return f"{lower_bound}-{upper_bound}sec"
            else:
                return self.get_fallback_category()
        except (AttributeError, TypeError):
            return self.get_fallback_category()

    def get_order(self) -> int:
        return self._order

    def get_name(self) -> str:
        return "duration"

    def is_applicable(self, file: "File") -> bool:
        try:
            return (
                hasattr(file.metadata, "duration")
                and file.metadata.duration is not None
                and file.metadata.duration >= 0
            )
        except Exception:
            return False


class DateCreatedFilter(Filter):
    """Filters files by creation date using configurable date formats."""

    def __init__(self, date_format: str = "%Y-%m", order: int = 4):
        self.date_format = date_format
        self._order = order

    def get_category(self, file: "File") -> str:
        try:
            import datetime

            stat = os.stat(file.path)
            created_time = stat.st_birthtime
            date = datetime.datetime.fromtimestamp(created_time)
            return date.strftime(self.date_format)
        except Exception:
            return "unknown_date"

    def get_order(self) -> int:
        return self._order

    def get_name(self) -> str:
        return "date_created"

    def is_applicable(self, file: "File") -> bool:
        return True


class ExtensionFilter(Filter):
    """Filters files by their file extension."""

    def __init__(self, order: int = 0):
        self._order = order
        print(f"ExtensionFilter created with order: {order}")

    def get_category(self, file: "File") -> str:
        if not file.extension:
            return "no_extension"
        return file.extension.lower().replace(".", "")

    def get_order(self) -> int:
        return self._order

    def get_name(self) -> str:
        return "extension"

    def is_applicable(self, file: "File") -> bool:
        return True


class ResolutionFilter(Filter):
    """Filters files by resolution dimensions.

    Primarily used for image and video files.
    """

    def __init__(self, order: int = 0):
        self._order = order
        print(f"ResolutionFilter created with order: {order}")

    def get_category(self, file: "File") -> str:
        metadata = file.metadata
        if hasattr(metadata, "dimensions") and metadata.dimensions != (0, 0):
            width, height = metadata.dimensions
            return f"{width}x{height}"
        elif hasattr(metadata, "resolution") and metadata.resolution != (0, 0):
            width, height = metadata.resolution
            return f"{width}x{height}"
        else:
            return self.get_fallback_category()

    def get_order(self) -> int:
        return self._order

    def get_name(self) -> str:
        return "resolution"

    def is_applicable(self, file: "File") -> bool:
        try:
            if hasattr(file.metadata, "dimensions"):
                return file.metadata.dimensions != (0, 0)
            elif hasattr(file.metadata, "resolution"):
                return file.metadata.resolution != (0, 0)
            return False
        except Exception:
            return False
