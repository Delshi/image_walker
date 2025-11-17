class FileMetadata:
    """Base class for file metadata.

    Attributes:
        size_bytes: File size in bytes.
    """

    def __init__(self, size_bytes: int):
        self.size_bytes = size_bytes


class ImageMetadata(FileMetadata):
    """Metadata specific to image files.

    Attributes:
        dimensions: Image dimensions as (width, height) tuple.
        format_: Image format (e.g., 'JPEG', 'PNG').
    """

    def __init__(self, size_bytes: int, dimensions: tuple[int, int], format_: str):
        super().__init__(size_bytes)
        self.dimensions = dimensions
        self.format_ = format_


class VideoMetadata(FileMetadata):
    """Metadata specific to video files.

    Attributes:
        duration: Video duration in seconds.
        resolution: Video resolution as (width, height) tuple.
        codec: Video codec information.
    """

    def __init__(
        self, size_bytes: int, duration: float, resolution: tuple[int, int], codec: str
    ):
        super().__init__(size_bytes)
        self.duration = duration  # в секундах
        self.resolution = resolution
        self.codec = codec


class DocumentMetadata(FileMetadata):
    """Metadata specific to document files.

    Attributes:
        page_count: Number of pages in the document.
        author: Document author if available.
    """

    def __init__(self, size_bytes: int, page_count: int, author: str = ""):
        super().__init__(size_bytes)
        self.page_count = page_count
        self.author = author


class AudioMetadata(FileMetadata):
    """Metadata specific to audio files.

    Attributes:
        duration: Audio duration in seconds.
        format_: Audio format (e.g., 'MP3', 'WAV').
    """

    def __init__(self, size_bytes: int, duration: float, format_: str):
        super().__init__(size_bytes)
        self.duration = duration  # в секундах
        self.format_ = format_
