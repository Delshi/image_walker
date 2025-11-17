from dataclasses import dataclass
from typing import Dict, Any
from imagewalker.domain.file_system_domain import File
from imagewalker.plugins.interface import (
    BaseFilterPlugin,
    PluginConfig,
    template_plugin,
)
from imagewalker.plugins.registry import PluginRegistry
from imagewalker.filters.filters import Filter


@dataclass
class FileTypeConfig(PluginConfig):
    """Configuration for file type grouping plugin.

    Attributes:
        group_images: Whether to group image files.
        group_videos: Whether to group video files.
        group_audio: Whether to group audio files.
        group_documents: Whether to group document files.
    """

    group_images: bool = True
    group_videos: bool = True
    group_audio: bool = True
    group_documents: bool = True


@template_plugin
@PluginRegistry.register("file_type")
class FileTypePlugin(BaseFilterPlugin):
    """Plugin for grouping files by general file types (images, videos, etc)."""

    def create_filter(self, config: Dict[str, Any]):
        return FileTypeFilter(
            order=config.get("order", 0),
            group_images=config.get("group_images", True),
            group_videos=config.get("group_videos", True),
            group_audio=config.get("group_audio", True),
            group_documents=config.get("group_documents", True),
        )

    @classmethod
    def get_config_class(cls):
        return FileTypeConfig


class FileTypeFilter(Filter):
    """Filter that categorizes files by general type categories."""

    def __init__(
        self,
        group_images: bool = True,
        group_videos: bool = True,
        group_audio: bool = True,
        group_documents: bool = True,
        order: int = 0,
    ):
        self.group_images = group_images
        self.group_videos = group_videos
        self.group_audio = group_audio
        self.group_documents = group_documents
        self._order = order

        self.image_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".webp",
            ".tiff",
        }
        self.video_extensions = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"}
        self.audio_extensions = {".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"}
        self.document_extensions = {".pdf", ".doc", ".docx", ".txt", ".rtf"}

    def get_category(self, file: "File") -> str:
        ext = file.extension.lower()

        if self.group_images and ext in self.image_extensions:
            return "images"
        elif self.group_videos and ext in self.video_extensions:
            return "videos"
        elif self.group_audio and ext in self.audio_extensions:
            return "audio"
        elif self.group_documents and ext in self.document_extensions:
            return "documents"
        else:
            return "other_files"

    def get_order(self) -> int:
        return self._order

    def get_name(self) -> str:
        return "file_type"

    def is_applicable(self, file: "File") -> bool:
        return True
