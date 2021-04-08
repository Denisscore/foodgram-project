"""Формы приложения Recipes."""
from django import forms

from recipes.models import Product, Recipe, Tag


class RecipeForm(forms.ModelForm):
    """Форма для создания и редактирования рецепта."""

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'tags__checkbox'}),
        to_field_name='slug',
        required=False
    )
    description = forms.CharField(required=True)

    class Meta:
        """Определяем для формы модель, необходимые поля и виджеты."""

        model = Recipe
        fields = (
            'name', 'tags', 'cook_time', 'ingredients', 'description',
            'image',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form__input'}),
            'cook_time': forms.NumberInput(
                attrs={'class': 'form__input', 'id': 'id_time',
                       'name': 'time'}),
            'description': forms.Textarea(
                attrs={'class': 'form__textarea', 'rows': '8'}),
        }
        labels = {
            'image': 'Загрузить фото'
        }

    def clean_ingredients(self):
        """Валидатор для ингредиентов."""
        ingredient_names = self.data.getlist('nameIngredient')
        ingredient_units = self.data.getlist('unitsIngredient')
        ingredient_amounts = self.data.getlist('valueIngredient')
        ingredients_clean = []
        for ingredient in zip(ingredient_names, ingredient_units,
                              ingredient_amounts):
            if not int(ingredient[2]) > 0:
                raise forms.ValidationError('Количество ингредиентов должно '
                                            'быть положительным и не нулевым')
            elif not Product.objects.filter(title=ingredient[0]).exists():
                raise forms.ValidationError(
                    'Ингредиенты должны быть из списка')
            else:
                ingredients_clean.append({'title': ingredient[0],
                                          'unit': ingredient[1],
                                          'amount': ingredient[2]})
        if len(ingredients_clean) == 0:
            raise forms.ValidationError('Добавьте ингредиент')
        return ingredients_clean

    def clean_name(self):
        """Валидатор для названия рецептов."""
        data = self.cleaned_data['name']
        if len(data) == 0:
            raise forms.ValidationError('Добавьте название рецепта')
        return data

    def clean_description(self):
        """Валидатор для описания рецептов рецептов."""
        data = self.cleaned_data['description']
        if len(data) == 0:
            raise forms.ValidationError('Добавьте описание рецепта')
        return data

    def clean_tags(self):
        """Валидатор для описания рецептов рецептов."""
        data = self.cleaned_data['tags']
        if len(data) == 0:
            raise forms.ValidationError('Добавьте тег')
        return data
