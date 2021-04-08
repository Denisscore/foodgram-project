"""Бизнес логика для приложения Recipes."""
from recipes.models import Product, Ingredient


def get_ingredients_from_form(ingredients, recipe):
    """Получает ингредиенты рецепта из формы и возвращает их списком."""
    ingredients_for_save = []
    for ingredient in ingredients:
        product = Product.objects.get(title=ingredient['title'])
        ingredients_for_save.append(
            Ingredient(recipe=recipe, ingredient=product,
                       amount=ingredient['amount']))
    return ingredients_for_save
