from imagewalker.providers.walker_service_provider import get_walker_service
from imagewalker.repository.walker_repo import WalkerRepository

# from imagewalker.utils.print_objective_tree import print_tree

source = "D:\\Desktop\\to_sort"
destination = "D:\\Desktop\\to_sort\\sorted"


def main():
    """Main entry point for the ImageWalker application.

    Initializes the WalkerService, configures filters, and executes file sorting.

    Raises:
        Exception: If any error occurs during the sorting process.
    """
    try:
        allowed_ext = [
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
        ]

        walker = get_walker_service(
            walker_repo=WalkerRepository,
            source_path=source,
            allowed_ext=allowed_ext,
        )

        available_filters = walker.get_available_filters_with_info()
        print("Available filters:")
        for name, info in available_filters.items():
            print(f"   - {name}")

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

        result_tree = walker.sort_by(
            filters_config=filters_config,
            dest=destination,
        )

        # print_tree(result_tree)

    except Exception as e:
        print(f"Error in main: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
