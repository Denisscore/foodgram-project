"""Описание страницы администратора для приложения Recipes."""
from django.contrib import admin

from recipes.models import Favorite, Ingredient, Product, Purchase, Recipe, Tag


class IngredientInline(admin.TabularInline):
    """Описание полей модели Ingredient для сайта администрирования."""

    model = Ingredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    """Описание полей модели Recipe для сайта администрирования."""

    model = Recipe
    list_display = ('pk', 'author', 'name', 'in_favorite_count',)
    list_filter = ('name', 'author', 'tags')
    inlines = (IngredientInline,)

    def in_favorite_count(self, obj):
        """Возвращает сколько раз рецепт находится в избранном."""
        return obj.favorite_set.count()

    in_favorite_count.short_description = 'В избранном'


class ProductAdmin(admin.ModelAdmin):
    """Описание полей модели Product для сайта администрирования."""

    model = Product
    list_display = ('pk', 'title', 'unit',)
    list_filter = ('title',)


class FavoriteAdmin(admin.ModelAdmin):
    """Описание полей модели Favorite для сайта администрирования."""

    model = Favorite
    list_display = ('pk', 'user', 'show_recipes',)

    def show_recipes(self, obj):
        """Возвращает названия избранных рецептов."""
        recipes = obj.recipes.all()
        return '\n'.join([recipe.name for recipe in recipes])


class PurchaseAdmin(admin.ModelAdmin):
    """Описание полей модели Purchase для сайта администрирования."""

    model = Favorite
    list_display = ('pk', 'user', 'show_recipes',)

    def show_recipes(self, obj):
        """Возвращает названия избранных рецептов."""
        recipes = obj.recipes.all()
        return '\n'.join([recipe.name for recipe in recipes])


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Tag)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Purchase, PurchaseAdmin)
