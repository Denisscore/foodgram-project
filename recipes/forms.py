from django import forms

from recipes.models import Product, Recipe, Tag


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
        for name, unit, amount in zip(ingredient_names, ingredient_units,
                              ingredient_amounts):
            if not int(amount) > 0:
                raise forms.ValidationError('Количество ингредиентов должно '
                                            'быть положительным и не нулевым')
            elif not Product.objects.filter(title=name).exists():
                raise forms.ValidationError(
                    'Ингредиенты должны быть из списка')
            else:
                ingredients_clean.append({'title': name,
                                          'unit': unit,
                                          'amount': amount})
        if len(ingredients_clean) == 0:
            raise forms.ValidationError('Добавьте ингредиент')
        return ingredients_clean

    def clean_tags(self):
        data = self.cleaned_data['tags']
        if len(data) == 0:
            raise forms.ValidationError('Добавьте тег')
        return data
