ImageWalker Documentation
=========================

**ImageWalker** - мощный инструмент для сортировки любых файлов с поддержкой плагинов-фильтров.

Быстрый старт
-------------

Основные возможности:

- Рекурсивный обход файловой системы
- Гибкая система фильтров  
- Поддержка пользовательских плагинов
- Сбор статистики по файлам
- Расширяемая архитектура

.. code-block:: python

   from imagewalker.providers.walker_service_provider import get_walker_service
   from imagewalker.repository.walker_repo import WalkerRepository 
   
   source = "path\\to\\target"
   destination = "path\\to\\destination"

   allowed_ext = [".MP4", ".PNG", ".PDF", ".ETC"]

   walker = get_walker_service(
        walker_repo=WalkerRepository,
        source_path=source,
        allowed_ext=allowed_ext,
   )

   filters_config = [
        {"name": "file_type", "order": 0},
        {"name": "extension", "order": 1},
        {"name": "resolution", "order": 2},
        {"name": "your_favorite_filter", "order": 3, "param1": "value1", "param2": "value2", "etc": "etc"}
   ]

   walker.sort_by(
        filters_config=filters_config,
        dest=destination,
   )

Основные модули
---------------

.. toctree::
   :maxdepth: 2
   :caption: Документация:

   modules/core
   modules/services
   modules/filters
   modules/plugins
   modules/repository

Дополнительные модули
---------------------

.. toctree::
   :maxdepth: 1
   
   modules/utils

Индексы и таблицы
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
