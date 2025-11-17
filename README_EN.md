# ImageWalker

**ImageWalker** is a flexible and extensible tool for automatic file sorting into categories based on their metadata: type, extension, resolution, size, date, and other parameters. Supports images, videos, audio, documents, and any other file formats.

**Language**: [English](README_EN.md) | [Русский](README.md)

---

## Features

- **Automatic file classification** by:
  - Type (images, videos, audio, documents, etc.)
  - Extension (`.jpg`, `.mp4`, `.pdf`, etc.)
  - Resolution (`1920x1080`, `640x480`, etc.)
  - File size (`0.0–10.0_MB`, `10.0–20.0_MB`, etc.)
  - Duration (for audio/video)
  - Creation or modification date
- **Custom filter support** through plugin system
- **Multi-level sorting structure** - combine filters in specified order
- **Safe file copying** with original metadata preservation
- **Detailed statistics** on processed files and applied filters

---

## Supported Formats

| Type          | Formats                                                                 |
| ------------- | ----------------------------------------------------------------------- |
| **Images**    | `JPEG`, `PNG`, `GIF`, `WEBP`, `TIFF`, `BMP`, `ICO`, `SVG`, `RAW`, `EPS` |
| **Video**     | `MP4`, `AVI`, `MKV`, `MOV`, `WMV`, `FLV`, `WEBM`                        |
| **Audio**     | `MP3`, `WAV`, `OGG`, `FLAC`, `AAC`, `M4A`                               |
| **Documents** | `PDF`, `DOC`, `DOCX`, `TXT`                                             |
| **Other**     | `PY` and other formats not listed above (processed as regular files)    |

> Metadata extraction uses external libraries (`Pillow`, `OpenCV`, `pydub`, `moviepy`, `PyPDF2`, etc.), but files are still processed with basic data even if these libraries are missing.

> To add other formats, simply include them in the corresponding lists in `ImageWalker\imagewalker\domain\file_system_domain.py`

---

## Quick Start

1. **Clone the repository** or install the project locally.
2. Configure paths in `main.py`:

```python
source = "path\\to\\target"
destination = "path\\to\\result"
```

3. Specify desired filters:

```python
filters_config = [
    {"name": "file_type", "order": 0},
    {"name": "extension", "order": 1},
    {"name": "resolution", "order": 2},
]
```

4. And run:

```python
python -m imagewalker.main
```

Files from source will be copied into a hierarchical structure in destination, for example:

```bash
sorted/
└── images/
    └── jpg/
        └── 1920x1080/
            ├── photo1.jpg
            └── photo2.jpg
```

## Plugins and Extensions

### mageWalker supports a plugin system:

**Built-in filters**: extension, resolution, byte_size, duration, date_created

**Plugins**: file_type, date_range, custom_size (you can add your own!)

> Plugins are automatically loaded from imagewalker/plugins/custom_filters/. To create your own filter, implement BaseFilterPlugin and use the @PluginRegistry.register("my_filter") decorator.

## Requirements

- Python 3.8+

- Pillow — for images

- opencv-python — alternative video/image analysis

- pydub + ffmpeg — for audio

- moviepy — for video

- PyPDF2 — for PDF

- python-docx — for DOCX

## Example Output

```bash
Available filters:
   - extension
   - byte_size
   - duration
   - resolution
   - date_created
   - file_type
   - date_range

Found source tree with 142 files
Target directory: D:\Desktop\to_sort\sorted
Sorting completed successfully

RESULT:
   Total files processed: 142
   Skipped files: 0

   Files applicable to each filter:
     file_type: 142 files (100.0%)
     extension: 142 files (100.0%)
     resolution: 98 files (69.0%)
     ...
```

## License

> Free to use, contribute and copy
