import csv
import os

from typing import Optional
from django.core.management.base import BaseCommand
from django.db import models

from api_yamdb.settings import BASE_DIR
from reviews.models import (
    Category,
    Comment,
    CustomUser,
    Genre,
    GenreTitle,
    Review,
    Title
)

STATIC_DIR_NAME = 'static'
DATA_DIR_NAME = 'data'
FULL_DIR = BASE_DIR / STATIC_DIR_NAME / DATA_DIR_NAME

CSV_TO_MODEL_MAPPING: dict[str, models.Model] = {
    'users.csv': CustomUser,
    'category.csv': Category,
    'genre.csv': Genre,
    'titles.csv': Title,
    'genre_title.csv': GenreTitle,
    'review.csv': Review,
    'comments.csv': Comment,
}


class Command(BaseCommand):
    """Описание команды dataloader."""

    def handle(self, *args, **options) -> Optional[str]:
        """Основное действие при выполнение команды."""

        # Проверяем пути
        try:
            self.check_dir(STATIC_DIR_NAME, BASE_DIR)
            self.check_dir(DATA_DIR_NAME, STATIC_DIR_NAME)
            csv_files = self.find_csv_files()
        except Exception as exception:
            # Текст ошибки слишком большой, можно проще:
            return exception

        # Ищем доступные файлы
        valid_csv_files = []
        print('Проверка файлов и моделей')
        for filename in CSV_TO_MODEL_MAPPING:
            if filename in csv_files:
                valid_csv_files.append(filename)
                model = CSV_TO_MODEL_MAPPING.get(filename)
                # Можно через colorama цвет покрасить =)
                print(f'  > {filename} для {model.__qualname__} - найден.')
            else:
                return 'Проверьте CSV_TO_MODEL_MAPPING'

        # Берем валидный файл (для которого описана выше модель)
        print('Начинаем загрузку данных:')
        for filename in valid_csv_files:
            try:
                model = CSV_TO_MODEL_MAPPING.get(filename)
                print(f'  > {filename} - ', end='')
                with open(FULL_DIR / filename, 'r', encoding='utf-8') as data:
                    for line in csv.DictReader(data):
                        # Для некоторых пришлось создать менеджер с этой
                        # командой, т.к. файлы "грязные"
                        if hasattr(model.objects, 'create_object'):
                            model.objects.create_object(**line)
                        # Там, где менеджера нет - подойдет обычный save
                        else:
                            instance = model(**line)
                            instance.save()
                print('успешно загружен.')
            except Exception as e:
                print(f'ошибка: {e}')
                continue
        return 'Данные успешно загружены'

    def check_dir(self, dir, path):
        """Проверка пути."""
        static_dir = os.path.join(path, dir)
        if not os.path.exists(static_dir):
            raise Exception(f'Путь {static_dir} не существует')

    def find_csv_files(self) -> list[str]:
        """Поиск csv-файлов."""
        DIR = f'{STATIC_DIR_NAME}/{DATA_DIR_NAME}'
        csv_files = [
            file for file in os.listdir(DIR) if file.endswith('.csv')
        ]
        if not csv_files:
            raise Exception(f'Не найдены CSV-файлы в дирректории {DIR}')
        return csv_files
