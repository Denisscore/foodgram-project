from django.shortcuts import get_object_or_404

from recipes.models import Ingredient, Product


def get_ingredients_from_form(ingredients, recipe):
    ingredients_for_save = []
    for ingredient in ingredients:
        product = get_object_or_404(Product, title=ingredient['title'])
        ingredients_for_save.append(
            Ingredient(recipe=recipe, ingredient=product,
                       amount=ingredient['amount']))
    return ingredients_for_save
