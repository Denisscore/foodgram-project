"""Файлом конфигурации для самого приложения api."""
from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """
    Подключение приложения api.

    Для настройки приложения создаем класс наследник AppConfig и указываем
    путь для его импорта в INSTALLED_APPS.

    """

    name = 'recipes'
