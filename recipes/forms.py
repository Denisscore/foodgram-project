from django import forms

from recipes.models import Product, Recipe, Tag, Ingredient
from recipes.utils import get_ingredients_from_form


class RecipeForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'tags__checkbox'}),
        to_field_name='slug',
        required=False
    )
    description = forms.CharField(required=True)

    class Meta:
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
        ingredient_names = self.data.getlist('nameIngredient')
        ingredient_units = self.data.getlist('unitsIngredient')
        ingredient_amounts = self.data.getlist('valueIngredient')
        ingredients_clean = []
        counts = 0
        for name, unit, amount in zip(ingredient_names, ingredient_units,
                                      ingredient_amounts):
            if not int(amount) > 0:
                raise forms.ValidationError('Количество ингредиентов должно '
                                            'быть положительным и не нулевым')
            elif not Product.objects.filter(title=name).exists():
                raise forms.ValidationError('Ингредиенты должны быть из списка')
            else:
                ingredients_clean.append({'title': name,
                                          'unit': unit,
                                          'amount': amount})
        for ing_dict in ingredients_clean:
            if ingredient_names[0] in ing_dict.values():
                counts += 1
            if counts > 1:
                raise forms.ValidationError('Не должно быть одинаковых ингредиентов,'
                                            'при необходимости увеличте количество нужного вам ингредиента')
        if len(ingredients_clean) == 0:
            raise forms.ValidationError('Добавьте ингредиент')
        return ingredients_clean

    def clean_tags(self):
        data = self.cleaned_data['tags']
        if len(data) == 0:
            raise forms.ValidationError('Добавьте тег')
        return data

    '''def save(self):
        self.instance = super().save(commit=False)
        self.instance.ingredients.remove()
        self.instance.amounts.all().delete()
        ingredients = self.cleaned_data['ingredients']
        self.cleaned_data['ingredients'] = []
        Ingredient.objects.bulk_create(
            get_ingredients_from_form(ingredients, self.instance))
        self.save_m2m()
        return self.instance'''
