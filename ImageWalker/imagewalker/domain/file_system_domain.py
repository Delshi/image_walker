import os
from abc import ABC
from pathlib import Path
from typing import Generic, List, Optional, Tuple, TypeVar

try:
    from PIL import Image, ImageFile

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2

    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    from pydub import AudioSegment
    from pydub.utils import mediainfo

    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

try:
    import PyPDF2

    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    from moviepy.editor import VideoFileClip

    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

from imagewalker.domain.files_metadata import (
    AudioMetadata,
    DocumentMetadata,
    FileMetadata,
    ImageMetadata,
    VideoMetadata,
)

T = TypeVar("T")


class FileSystemNode(ABC):
    """Abstract base class representing a node in the file system hierarchy.

    Attributes:
        name: Name of the file system node.
        path: Full path to the file system node.
    """

    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path


class Directory(FileSystemNode):
    """Represents a directory in the file system.

    Attributes:
        subdirectories: List of subdirectories within this directory.
        files: List of files contained in this directory.
    """

    def __init__(self, name: str, path: str):
        super().__init__(name, path)
        self.subdirectories: List["Directory"] = []
        self.files: List["File"] = []

    def add_subdirectory(self, directory: "Directory"):
        """Adds a subdirectory to this directory.

        Args:
            directory: Directory instance to add as subdirectory.
        """
        self.subdirectories.append(directory)

    def add_file(self, file: "File"):
        """Adds a file to this directory.

        Args:
            file: File instance to add to directory.
        """
        self.files.append(file)

    def find_directory(self, path_parts: List[str]) -> Optional["Directory"]:
        """Recursively finds a directory by path parts.

        Args:
            path_parts: List of directory names representing the path.

        Returns:
            Directory instance if found, None otherwise.
        """
        if not path_parts:
            return self

        target_dir = path_parts[0]
        for subdir in self.subdirectories:
            if subdir.name == target_dir:
                return subdir.find_directory(path_parts[1:])

        return None


class File(FileSystemNode, Generic[T]):
    """Generic file class supporting any file type with metadata.

    Attributes:
        extension: File extension in uppercase.
        metadata: Typed metadata specific to the file type.
    """

    def __init__(self, name: str, path: str, extension: str, metadata: T):
        super().__init__(name, path)
        self.extension = extension
        self.metadata = metadata


class FileFactory:
    """Factory class for creating File objects with appropriate metadata."""

    @staticmethod
    def create_file(file_path: str) -> File:
        """Creates a File object with appropriate metadata based on file type.

        Args:
            file_path: Path to the file to be processed.

        Returns:
            File object with populated metadata.

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        try:
            path_obj = Path(file_path)
            name = path_obj.name
            extension = path_obj.suffix.upper() if path_obj.suffix else ""

            if not path_obj.exists():
                raise FileNotFoundError(f"File {file_path} does not exist")

            stat = path_obj.stat()
            size_bytes = stat.st_size

            image_extensions = [
                ".JPG",
                ".JPEG",
                ".PNG",
                ".GIF",
                ".WEBP",
                ".BMP",
                ".TIFF",
                ".ICO",
                ".SVG",
                ".RAW",
                ".EPS",
            ]
            video_extensions = [".MP4", ".AVI", ".MKV", ".MOV", ".WMV", ".FLV", ".WEBM"]
            audio_extensions = [".MP3", ".WAV", ".OGG", ".FLAC", ".AAC", ".M4A"]
            document_extensions = [".PDF", ".DOC", ".DOCX", ".TXT"]

            if extension in image_extensions:
                dimensions = FileFactory._get_image_dimensions(file_path)
                metadata = ImageMetadata(
                    size_bytes, dimensions, extension[1:] if extension else "unknown"
                )

            elif extension in video_extensions:
                duration, resolution = FileFactory._get_video_info(file_path)
                metadata = VideoMetadata(size_bytes, duration, resolution, "unknown")

            elif extension in audio_extensions:
                duration = FileFactory._get_audio_duration(file_path)
                metadata = AudioMetadata(
                    size_bytes, duration, extension[1:] if extension else "unknown"
                )

            elif extension in document_extensions:
                page_count = FileFactory._get_document_info(file_path)
                metadata = DocumentMetadata(size_bytes, page_count)

            else:
                metadata = FileMetadata(size_bytes)

            return File(name, str(file_path), extension, metadata)

        except Exception as e:
            print(f"Error creating file object for {file_path}: {e}")
            # Возвращаем файл с базовыми метаданными
            return File(Path(file_path).name, str(file_path), "", FileMetadata(0))

    @staticmethod
    def _get_image_dimensions(file_path: str) -> Tuple[int, int]:
        """Extracts dimensions from image files.

        Args:
            file_path: Path to the image file.

        Returns:
            Tuple of (width, height) in pixels.
        """
        try:
            if PIL_AVAILABLE:
                try:
                    # Включаем обработку частично загруженных изображений
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    with Image.open(file_path) as img:
                        return img.size
                except Exception as e:
                    print(f"PIL failed for {file_path}: {e}")

            if OPENCV_AVAILABLE:
                try:
                    img = cv2.imread(file_path)
                    if img is not None:
                        height, width = img.shape[:2]
                        return (width, height)
                except Exception as e:
                    print(f"OpenCV failed for {file_path}: {e}")

            try:
                if os.name == "posix":  # Linux/Mac
                    import subprocess

                    result = subprocess.run(
                        ["identify", "-format", "%wx%h", file_path],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if result.returncode == 0:
                        width, height = map(int, result.stdout.strip().split("x"))
                        return (width, height)
            except Exception:
                pass

        except Exception as e:
            print(f"Error getting image dimensions for {file_path}: {e}")

        return (0, 0)

    @staticmethod
    def _get_video_info(file_path: str) -> Tuple[float, Tuple[int, int]]:
        """Extracts duration and resolution from video files.

        Args:
            file_path: Path to the video file.

        Returns:
            Tuple of (duration_seconds, (width, height)).
        """
        duration = 0.0
        resolution = (0, 0)

        try:
            if MOVIEPY_AVAILABLE:
                try:
                    with VideoFileClip(file_path) as video:
                        duration = video.duration
                        resolution = (video.w, video.h)
                        return (duration, resolution)
                except Exception as e:
                    print(f"MoviePy failed for {file_path}: {e}")

            if OPENCV_AVAILABLE:
                try:
                    cap = cv2.VideoCapture(file_path)
                    if cap.isOpened():
                        # Получаем FPS и количество кадров для вычисления длительности
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                        if fps > 0 and frame_count > 0:
                            duration = frame_count / fps

                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        resolution = (width, height)

                        cap.release()
                        return (duration, resolution)
                except Exception as e:
                    print(f"OpenCV video failed for {file_path}: {e}")

            try:
                import json
                import subprocess

                # Команда для получения информации о видео в JSON формате
                cmd = [
                    "ffprobe",
                    "-v",
                    "quiet",
                    "-print_format",
                    "json",
                    "-show_format",
                    "-show_streams",
                    file_path,
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    info = json.loads(result.stdout)

                    # Ищем видеопоток
                    for stream in info.get("streams", []):
                        if stream.get("codec_type") == "video":
                            width = stream.get("width", 0)
                            height = stream.get("height", 0)
                            resolution = (width, height)
                            break

                    # Получаем длительность из формата
                    format_info = info.get("format", {})
                    if "duration" in format_info:
                        duration = float(format_info["duration"])

            except Exception as e:
                print(f"FFprobe failed for {file_path}: {e}")

        except Exception as e:
            print(f"Error getting video info for {file_path}: {e}")

        return (duration, resolution)

    @staticmethod
    def _get_audio_duration(file_path: str) -> float:
        """Extracts duration from audio files.

        Args:
            file_path: Path to the audio file.

        Returns:
            Duration in seconds.
        """
        try:
            if PYDUB_AVAILABLE:
                try:
                    audio = AudioSegment.from_file(file_path)
                    return (
                        len(audio) / 1000.0
                    )  # pydub возвращает длительность в миллисекундах
                except Exception as e:
                    print(f"Pydub failed for {file_path}: {e}")

            try:
                from mutagen import File

                audio = File(file_path)
                if audio is not None:
                    return audio.info.length
            except ImportError:
                pass
            except Exception as e:
                print(f"Mutagen failed for {file_path}: {e}")

            try:
                import json
                import subprocess

                cmd = [
                    "ffprobe",
                    "-v",
                    "quiet",
                    "-print_format",
                    "json",
                    "-show_format",
                    file_path,
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    duration_str = info.get("format", {}).get("duration")
                    if duration_str:
                        return float(duration_str)

            except Exception as e:
                print(f"FFprobe audio failed for {file_path}: {e}")

        except Exception as e:
            print(f"Error getting audio duration for {file_path}: {e}")

        return 0.0

    @staticmethod
    def _get_document_info(file_path: str) -> int:
        """Extracts information from document files.

        Args:
            file_path: Path to the document file.

        Returns:
            Estimated page count for the document.
        """
        try:
            extension = Path(file_path).suffix.upper()

            if extension == ".PDF" and PYPDF2_AVAILABLE:
                try:
                    with open(file_path, "rb") as file:
                        reader = PyPDF2.PdfReader(file)
                        return len(reader.pages)
                except Exception as e:
                    print(f"PyPDF2 failed for {file_path}: {e}")

            if extension in [".DOC", ".DOCX"]:
                try:
                    import docx

                    doc = docx.Document(file_path)
                    return len(doc.paragraphs)
                except ImportError:
                    pass
                except Exception as e:
                    print(f"python-docx failed for {file_path}: {e}")

            if extension == ".TXT":
                try:
                    with open(
                        file_path, "r", encoding="utf-8", errors="ignore"
                    ) as file:
                        content = file.read()
                        # Приблизительно 3000 символов на страницу
                        return max(1, len(content) // 3000)
                except Exception as e:
                    print(f"TXT processing failed for {file_path}: {e}")

        except Exception as e:
            print(f"Error getting document info for {file_path}: {e}")

        return 0
