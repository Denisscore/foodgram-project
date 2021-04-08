"""Модели приложения Recipes."""
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Product(models.Model):
    """Модель для хранения ингредиентов (продуктов)."""

    title = models.CharField(max_length=255, verbose_name='Название продукта')
    unit = models.CharField(max_length=64, verbose_name='Единицы измерения')

    def __str__(self):
        """Переопределяем строковое представление модели Product."""
        return '{title}, {unit}'.format(title=self.title, unit=self.unit)


class Tag(models.Model):
    """Модель тегов. Все возможные теги хранятся в этой модели."""

    name = models.CharField(max_length=100, verbose_name='Название тега')
    slug = models.SlugField(verbose_name='Слаг тега')
    colors = models.SlugField(verbose_name='Цвет тега', default='Black')

    def __str__(self):
        """Переопределяем строковое представление модели Tag."""
        return '{name}'.format(name=self.name)


class RecipeManager(models.Manager):
    """Менеджер реализует сортировку по тегам."""

    def tag_filter(self, tags):
        """
        Метод для работы с тегами.

        Возвращает выборку по тегам. Если теги не указаны то возвращает
        все рецепты.

        """
        if tags:
            return super().get_queryset().prefetch_related('author',
                                                           'tags').filter(
                tags__slug__in=tags).distinct()
        else:
            return super().get_queryset().prefetch_related('author',
                                                           'tags').all()


class Recipe(models.Model):
    """Модель для хранения рецептов."""

    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор рецепта',
                               related_name='recipe_author')

    name = models.CharField(max_length=255,
                            verbose_name='Название рецепта',
                            )

    description = models.TextField(verbose_name='Описание рецепта')

    image = models.ImageField(upload_to='recipes/',
                              verbose_name='Изображение блюда')

    tags = models.ManyToManyField(Tag, verbose_name='Теги',
                                  blank=True)

    ingredients = models.ManyToManyField(Product,
                                         through='Ingredient',
                                         related_name='recipe_ingredients',
                                         blank=True)

    cook_time = models.PositiveIntegerField(verbose_name='Время приготовления',
                                            validators=[MinValueValidator(1)],
                                            )

    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Время публикации',
                                    db_index=True)

    recipes = RecipeManager()

    class Meta:
        """Переопределяем сортировку по умолчанию."""

        ordering = ('-pub_date',)

    def __str__(self):
        """Переопределяем строковое представление модели Recipe."""
        return '{name}'.format(name=self.name)


class Ingredient(models.Model):
    """
    Модель для хранения ингредиентов.

    Модель связывает Recipe и Product. Какие ингредиенты (продукты) и сколько
    их нужно для конкретного рецепта.

    """

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_amount')
    ingredient = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(verbose_name='Количество ингредиента')

    class Meta:
        """
        Класс мета.

        Наборы имен полей, которые, взятые вместе, должны быть уникальными.
        """

        unique_together = ('ingredient', 'amount', 'recipe')

    def __str__(self):
        """Переопределяем строковое представление модели Recipe."""
        return '{amount}'.format(amount=self.amount)


class PurchaseManager(models.Manager):
    """Менеджер модели список покупок."""

    def counter(self, user):
        """Счетчик считает сколько рецептов в покупках."""
        try:
            return super().get_queryset().get(user=user).recipes.count()
        except ObjectDoesNotExist:
            return 0

    def get_purchases_list(self, user):
        """
        Список покупок.

        Функция возвращает QuerySet рецептов списка покупок. Если таких
        рецептов нет возвращает пустой лист.

        """
        try:
            return super().get_queryset().get(user=user).recipes.all()
        except ObjectDoesNotExist:
            return []


class Purchase(models.Model):
    """Модель для хранения рецептов выбранных для покупок."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipes = models.ManyToManyField(Recipe)

    purchase = PurchaseManager()


class FavoriteManager(models.Manager):
    """Менеджер модели избранное."""

    def get_tag_filtered(self, user, tags):
        """
        Получить отфильтрованные по тэгам рецепты.

        Функция возвращает QuerySet рецептов добавленных в избранное с учетом
        активных тегов. Если таких рецептов нет возвращает пустой лист.
        """
        try:
            recipes = super().get_queryset().get(user=user).recipes.all()
            if tags:
                return recipes.prefetch_related(
                    'author', 'tags'
                ).filter(
                    tags__slug__in=tags
                ).distinct()
            else:
                return recipes.prefetch_related(
                    'author', 'tags'
                ).all()
        except ObjectDoesNotExist:
            return []


class Favorite(models.Model):
    """Модель для хранения рецептов добавленных в избранное."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipes = models.ManyToManyField(Recipe)

    favorite = FavoriteManager()
