# ImageWalker

**ImageWalker** — это гибкий и расширяемый инструмент для автоматической сортировки файлов по категориям на основе их метаданных: типа, расширения, разрешения, размера, даты и других параметров. Поддерживает изображения, видео, аудио, документы и любые другие форматы.

**Language**: [English](README_EN.md) | [Русский](README.md)

---

## Возможности

- **Автоматическая классификация файлов** по:
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

## Поддерживаемые форматы

| Тип             | Форматы                                                                 |
| --------------- | ----------------------------------------------------------------------- |
| **Изображения** | `JPEG`, `PNG`, `GIF`, `WEBP`, `TIFF`, `BMP`, `ICO`, `SVG`, `RAW`, `EPS` |
| **Видео**       | `MP4`, `AVI`, `MKV`, `MOV`, `WMV`, `FLV`, `WEBM`                        |
| **Аудио**       | `MP3`, `WAV`, `OGG`, `FLAC`, `AAC`, `M4A`                               |
| **Документы**   | `PDF`, `DOC`, `DOCX`, `TXT`                                             |
| **Прочее**      | `PY` и другие, не перечисленные выше (обрабатываются как обычные файлы) |

> Для извлечения метаданных используются внешние библиотеки (`Pillow`, `OpenCV`, `pydub`, `moviepy`, `PyPDF2` и др.), но при их отсутствии файлы всё равно обрабатываются с базовыми данными.

> Для добавления других форматов достаточно добавить их в соответствующие списки в `ImageWalker\imagewalker\domain\file_system_domain.py`

---

## Быстрый старт

1. **Клонируйте репозиторий** или установите проект локально.
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
]
```

4. И запустите:

```python
python -m imagewalker.main
```

Файлы из source будут скопированы в иерархическую структуру в destination, например:

```bash
sorted/
└── images/
    └── jpg/
        └── 1920x1080/
            ├── photo1.jpg
            └── photo2.jpg
```

## Плагины и расширения

### ImageWalker поддерживает систему плагинов:

**Встроенные фильтры**: extension, resolution, byte_size, duration, date_created

**Плагины**: file_type, date_range, custom_size (можно добавлять свои!)

> Плагины автоматически загружаются из imagewalker/plugins/custom_filters/. Для создания собственного фильтра реализуйте BaseFilterPlugin и используйте декоратор @PluginRegistry.register("my_filter").

## Требования

- Python 3.8+

- Pillow — для изображений

- opencv-python — альтернативный анализ видео/изображений

- pydub + ffmpeg — для аудио

- moviepy — для видео

- PyPDF2 — для PDF

- python-docx — для DOCX

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

## Лицензия

> Free to use, contribute and copy
