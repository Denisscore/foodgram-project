from django.contrib import admin

from recipes.models import Favorite, Ingredient, Product, Purchase, Recipe, Tag


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    model = Recipe
    list_display = ('pk', 'author', 'name', 'in_favorite_count',)
    list_filter = ('name', 'author', 'tags')
    inlines = (IngredientInline,)

    def in_favorite_count(self, obj):
        return obj.favorite_set.count()

    in_favorite_count.short_description = 'В избранном'


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('pk', 'title', 'unit',)
    list_filter = ('title',)


class FavoriteAdmin(admin.ModelAdmin):
    model = Favorite
    list_display = ('pk', 'user', 'show_recipes',)

    def show_recipes(self, obj):
        recipes = obj.recipes.all()
        return ' '.join(recipes.values_list('name', flat=True))


class PurchaseAdmin(admin.ModelAdmin):
    model = Favorite
    list_display = ('pk', 'user', 'show_recipes',)

    def show_recipes(self, obj):
        recipes = obj.recipes.all()
        return ' '.join(recipes.values_list('name', flat=True))


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Tag)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Purchase, PurchaseAdmin)
