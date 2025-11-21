# ImageWalker

**Language**: [English](README_EN.md) | [Русский](README.md)

**ImageWalker** — это гибкий и расширяемый инструмент для автоматической сортировки файлов по категориям на основе их метаданных: типа, расширения, разрешения, размера, даты и других параметров. Поддерживает изображения, видео, аудио, документы и любые другие форматы.

---

- [Возможности](#возможности)
- [Плагины](#плагины)
- [AI-плагин](#ai-плагин)
- [Поддерживаемые форматы](#форматы)
- [Быстрый старт](#быстрый-старт)
- [Пример плагина](#пример-плагина)
- [Файловая структура](#файловая-структура)
- [Пример вывода](#вывод)
- [Документация](#документация)
- [Зависимости](#зависимости)
- [Лицензия](#лицензия)

---

## Возможности

- **Автоматическая классификация файлов** по:
  - Содержимому (на основе **кастомной сверточной нейросети**)
  - Типу (изображения, видео, аудио, документы и др.)
  - Расширению (`.jpg`, `.mp4`, `.pdf` и т.д.)
  - Разрешению (`1920x1080`, `640x480` и т.п.)
  - Размеру файла (`0.0–10.0_MB`, `10.0–20.0_MB` и т.д.)
  - Длительности (для аудио/видео)
  - Дате создания или изменения
- **Поддержка пользовательских фильтров** через систему плагинов
- **Многоуровневая структура сортировки** — можно комбинировать фильтры в заданном порядке
- **Безопасное копирование** файлов с сохранением исходных данных
- **Подробная статистика** по обработанным файлам и применённым фильтрам

---

## Плагины

### ImageWalker поддерживает систему плагинов:

**Встроенные фильтры**: extension, resolution, byte_size, duration, date_created

**Плагины**: **`neural_classifier`**, file_type, date_range, custom_size **(можно добавлять свои!)**

---

Плагины автоматически загружаются из imagewalker/plugins/custom_filters/. Для создания собственного фильтра реализуйте BaseFilterPlugin и используйте декоратор @PluginRegistry.register("my_filter").

## AI-плагин

Основан на моей <a href="https://github.com/Delshi/Intel-Image-Classification">**кастомной сверточной нейронной сети**</a>, которая классифицирует изображения по 6 классам из Intel Image Classification (buildings, forest, glacier, mountain, sea, streets).

<details><summary>Архитектура модели</summary>

![CNN Architecture](\ImageWalker\imagewalker\plugins\custom_filters\cnn_principal_scheme.png)

</details>

---

**Скачать модель или узнать подробнее об архитектуре, реализации и качестве можно здесь: https://github.com/Delshi/Intel-Image-Classification**

## Поддерживаемые форматы

| Тип             | Форматы                                                                        |
| --------------- | ------------------------------------------------------------------------------ |
| **Изображения** | `JPG`, `JPEG`, `PNG`, `GIF`, `WEBP`, `TIFF`, `BMP`, `ICO`, `SVG`, `RAW`, `EPS` |
| **Видео**       | `MP4`, `AVI`, `MKV`, `MOV`, `WMV`, `FLV`, `WEBM`                               |
| **Аудио**       | `MP3`, `WAV`, `OGG`, `FLAC`, `AAC`, `M4A`                                      |
| **Документы**   | `PDF`, `DOC`, `DOCX`, `TXT`                                                    |
| **Прочее**      | `PY` и другие, не перечисленные выше (обрабатываются как обычные файлы)        |

<details><summary>Полный список встроенных поддерживаемых форматов</summary>

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

Для извлечения метаданных используются внешние библиотеки (`Pillow`, `OpenCV`, `pydub`, `moviepy`, `PyPDF2` и др.), но при их отсутствии файлы всё равно обрабатываются с базовыми данными.

**_Для добавления других форматов достаточно добавить их в соответствующие списки в `ImageWalker\imagewalker\domain\file_system_domain.py`_**

---

## Быстрый старт

1. **Клонируйте репозиторий** или установите проект локально.

```bash
git clone https://github.com/Delshi/image_walker

poetry install
```

2. Настройте пути в `main.py`:

```python
source = "path\\to\\target"
destination = "path\\to\\result"
```

3. Укажите желаемые фильтры:

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

4. И запустите:

```python
python -m imagewalker.main
```

## Пример плагина

1. Импортируем необходимые зависимости.

```python
from dataclasses import dataclass
from typing import Dict, Any
from imagewalker.plugins.interface import (
    BaseFilterPlugin,
    PluginConfig,
    template_plugin,
)
from imagewalker.plugins.registry import PluginRegistry
from imagewalker.filters.filters import Filter
```

2. Описываем конфигурацию плагина. В конфигурации нужно описать все переменные, которые плагин может принимать на вход.

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

3. Делаем имплементацию фильтра, реализуя интерфейс `Filter`.

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

4. Делаем имплементацию своего плагина, реализуя интерфейс `BaseFilterPlugin`.

```python
@template_plugin
@PluginRegistry.register("custom_size")
class CustomSizePlugin(BaseFilterPlugin):
    """Plugin for custom file size grouping with configurable units."""

    def create_filter(self, config: Dict[str, Any]):
        unit = config.get("unit", "MB")
        step = config.get("custom_step", 5.0)

        # Конвертируем в байты
        unit_multipliers = {"KB": 1024, "MB": 1024 * 1024, "GB": 1024 * 1024 * 1024}

        step_bytes = int(step * unit_multipliers.get(unit, 1))

        return ByteSizeStepFilter(order=config.get("order", 0), step_bytes=step_bytes)

    @classmethod
    def get_config_class(cls):
        return CustomSizeConfig
```

## Файловая структура

Файлы из source будут скопированы в иерархическую структуру в destination, например:

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

## Пример вывода

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

## Документация

Полная документация по проекту и каждому модулю, классу и функции в веб-версии доступна по пути `\docs\build\html\index.html`

## Зависимости

- Python 3.8+

- Pillow — для изображений

- opencv-python — альтернативный анализ видео/изображений

- pydub + ffmpeg — для аудио

- moviepy — для видео

- PyPDF2 — для PDF

- python-docx — для DOCX

## Лицензия

> Free to use, contribute and copy
