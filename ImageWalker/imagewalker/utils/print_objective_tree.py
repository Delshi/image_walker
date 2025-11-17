from imagewalker.domain.file_system_domain import Directory


def print_tree(directory: Directory, level: int = 0):
    indent = "  " * level
    print(f"{indent}{directory.name}/")

    for file in directory.files:
        file_indent = "  " * (level + 1)
        metadata_info = ""

        if hasattr(file.metadata, "dimensions"):
            metadata_info = f" - {file.metadata.dimensions}"
        elif hasattr(file.metadata, "page_count"):
            metadata_info = f" - {file.metadata.page_count} pages"
        elif hasattr(file.metadata, "size_bytes"):
            metadata_info = f" - {file.metadata.size_bytes} bytes"

        print(f"{file_indent}{file.name}{metadata_info}")

    for subdir in directory.subdirectories:
        print_tree(subdir, level + 1)
