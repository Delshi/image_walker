# ImageWalker

**Language**: [English](README_EN.md) | [Русский](README.md)

**ImageWalker** is a flexible and extensible tool for automatically sorting files into categories based on their metadata: type, extension, resolution, size, date, and other parameters. It supports images, videos, audio, documents, and any other formats.

---

- [Features](#features)
- [Plugins](#plugins)
- [AI-plugin](#ai-plugin)
- [Supported formats](#supported-formats)
- [Quick start](#quick-start)
- [Plugin example](#plugin-example)
- [File structure](#file-structure)
- [Example output](#example-output)
- [Documentation](#documentation)
- [Requirements](#requirements)
- [License](#license)

---

## Features

- **Automatic file classification** by:
  - Its content (using **custom convolutional neural network**)
  - Type (image, video, audio, documents, etc.)
  - Extension (`.jpg`, `.mp4`, `.pdf`, etc.)
  - Resolution (`1920x1080`, `640x480`, etc.)
  - File size (`0.0–10.0_MB`, `10.0–20.0_MB`, etc.)
  - Duration (for audio/video)
  - Date created and updated
- **Support for custom filters** via plugin system
- **Multi-level sorting structure** — you can combine filters in a given order
- **Safely copy** files while preserving original data
- **Detailed statistics** on processed files and applied filters

---

## Plugins

### ImageWalker supports plugin system:

**Built-in filters**: extension, resolution, byte_size, duration, date_created

**Plugins**: **`neural_classifier`**, file_type, date_range, custom_size **(можно добавлять свои!)**

---

> Plugins are automatically loaded from `imagewalker/plugins/custom_filters/`.

> To create your own filter, implement `BaseFilterPlugin` and use the `@PluginRegistry.register("my_filter")` decorator.

## AI-plugin

Based on my <a href="https://github.com/Delshi/Intel-Image-Classification">**custom convolutional neural network**</a>, which classifies images into 6 classes from Intel Image Classification (buildings, forest, glacier, mountain, sea, streets).

<details><summary>Model's architecture</summary>

<img src="ImageWalker\imagewalker\plugins\custom_filters\cnn_principal_scheme.png" alt="CNN Architecture">

</details>

---

**You can download the model or learn more about the architecture, implementation, and quality here: https://github.com/Delshi/Intel-Image-Classification**

## Supported formats

| Type          | Formats                                                                        |
| ------------- | ------------------------------------------------------------------------------ |
| **Images**    | `JPG`, `JPEG`, `PNG`, `GIF`, `WEBP`, `TIFF`, `BMP`, `ICO`, `SVG`, `RAW`, `EPS` |
| **Video**     | `MP4`, `AVI`, `MKV`, `MOV`, `WMV`, `FLV`, `WEBM`                               |
| **Audio**     | `MP3`, `WAV`, `OGG`, `FLAC`, `AAC`, `M4A`                                      |
| **Documents** | `PDF`, `DOC`, `DOCX`, `TXT`                                                    |
| **Other**     | `PY` and others not listed above (processed as regular files)                  |

<details><summary>Full list of nuilt-in supported formats</summary>

    "JPEG",
    "JPG",
    "PNG",
    "GIF",
    "WEBP",
    "TIFF",
    "BMP",
    "ICO",
    "SVG",
    "RAW",
    "EPS",
    "MP4",
    "AVI",
    "MKV",
    "MOV",
    "MP3",
    "WAV",
    "OGG",
    "FLAC",
    "PDF",
    "DOC",
    "DOCX",
    "TXT",
    "PY",

</details>

---

External libraries (`Pillow`, `OpenCV`, `pydub`, `moviepy`, `PyPDF2`, etc.) are used to extract metadata, but if they are not available, files are still processed with the basic data.

**_To add other formats, simply add them to the appropriate lists in `ImageWalker\imagewalker\domain\file_system_domain.py`_**

---

## Quick start

1. **Clone git repository** or install project locally.

```bash
git clone https://github.com/Delshi/image_walker

poetry install
```

2. Confige your paths in `main.py`:

```python
source = "path\\to\\target"
destination = "path\\to\\result"
```

3. Choose prefered filters:

```python
filters_config = [
    {"name": "file_type", "order": 0},
    {"name": "extension", "order": 1},
    {"name": "resolution", "order": 2},
    {
        "name": "neural_classifier",
        "order": 3,
        "confidence_threshold": 0.8,
        "process_non_images": True,
    },
    {"name": "custom_size", "order": 4, "unit": "MB", "custom_step": 10},
    {"name": "date_range", "order": 5, "range_days": 7},
]
```

4. And launch:

```python
python -m imagewalker.main
```

## Plugin example

1. Import required dependencies

```python
from dataclasses import dataclass
from typing import Dict, Any
from imagewalker.plugins.interface import (
    BaseFilterPlugin,
    PluginConfig,
    template_plugin,
)
from imagewalker.plugins.registry import PluginRegistry
from imagewalker.filters.implementation import ByteSizeStepFilter
```

2. Describe the plugin configuration. The configuration should describe all the variables that the plugin can accept as input.

```python
@dataclass
class CustomSizeConfig(PluginConfig):
    """Configuration for custom size grouping plugin.

    Attributes:
        unit: Size unit ('KB', 'MB', 'GB').
        custom_step: Step size in the specified unit.
    """

    unit: str = "MB"
    custom_step: float = 5.0
```

3. Implement the filter by implementing the `Filter` interface

```python
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
```

4. Implement our plugin by implementing the `BaseFilterPlugin` interface.

```python
@template_plugin
@PluginRegistry.register("custom_size")
class CustomSizePlugin(BaseFilterPlugin):
    """Plugin for custom file size grouping with configurable units."""

    def create_filter(self, config: Dict[str, Any]):
        unit = config.get("unit", "MB")
        step = config.get("custom_step", 5.0)

        # Convert into bytes
        unit_multipliers = {"KB": 1024, "MB": 1024 * 1024, "GB": 1024 * 1024 * 1024}

        step_bytes = int(step * unit_multipliers.get(unit, 1))

        return ByteSizeStepFilter(order=config.get("order", 0), step_bytes=step_bytes)

    @classmethod
    def get_config_class(cls):
        return CustomSizeConfig
```

## File structure

Files from source will be copied into a hierarchical structure in destination, for example:

```bash
sorted/
└── images/
    └── jpg/
        └── 1920x1080/
            ├── photo1.jpg
            └── photo2.jpg
            2560x1440/
            ├── photo34.jpg
            └── photo43.jpg
        png/
        └── 1920x1080/
            ├── photo10.jpg
            └── photo21.jpg
            2560x1440/
            ├── photo52.jpg
            └── photo54.jpg
    videos/
    └── mp4/
        └── 1920x1080/
            ├── video1.jpg
            └── video2.jpg
            2560x1440/
            ├── video10.jpg
            └── video15.jpg
```

## Example output

```bash
Available filters:
   - extension
   - byte_size
   - duration
   - resolution
   - date_created
   - file_type
   - date_range

Found source tree with 121 files
Target directory: D:\Desktop\to_sort\sorted
Sorting completed successfully

RESULT:
   Total files processed: 121
   Skipped files: 0
   Total files processed: 121
   Skipped files: 0

   Files applicable to each filter:

   Files applicable to each filter:
   Files applicable to each filter:
     file_type: 121 files (100.0%)
     extension: 121 files (100.0%)
     resolution: 98 files (81.0%)
     neural_classifier: 121 files (100.0%)
     byte_size: 121 files (100.0%)
     date_range: 121 files (100.0%)
Sorting completed successfully
```

## Documentation

Full documentation for the project and each module, class, and function in the web version is available at `\docs\build\html\index.html`

## Requirements

- Python 3.8+

- Pillow — for images

- opencv-python — alternative video/image analysis

- pydub + ffmpeg — for audio

- moviepy — for video

- PyPDF2 — for PDF

- python-docx — for DOCX

## License

> Free to use, contribute and copy
