"""view приложения Recipes."""
import json
from urllib.parse import unquote

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods

from foodgram.settings import RECIPES_ON_PAGE
from recipes.forms import RecipeForm
from recipes.models import Favorite, Ingredient, Product, Purchase, Recipe
from recipes.utils import get_ingredients_from_form
from users.models import Subscription, User


class IndexView(View):
    """Главная страница сайта."""

    def get_queryset(self, request):
        """Запрос для главной страницы."""
        tags = request.GET.getlist('tag')
        recipes = Recipe.recipes.tag_filter(tags)
        return recipes

    def get(self, request):
        """Для главной страница сайта доступен только метод GET."""
        recipes = self.get_queryset(request)
        paginator = Paginator(recipes, RECIPES_ON_PAGE)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        context = {'title': 'Рецепты',
                   'page': page,
                   'paginator': paginator,
                   'purchase': Purchase.purchase,
                   }
        return render(request, 'recipes/indexAuth.html', context)


@login_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def new_recipe_view(request):
    """Создание нового рецепта."""
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        recipe = form.save(commit=False)
        recipe.author = request.user
        ingredients = form.cleaned_data['ingredients']
        form.cleaned_data['ingredients'] = []
        form.save()
        Ingredient.objects.bulk_create(
            get_ingredients_from_form(ingredients, recipe))
        return redirect('index_view')
    context = {'page_title': 'Создание рецепта',
               'button': 'Создать рецепт',
               'form': form,
               }
    return render(request, 'recipes/formRecipe.html', context)


@method_decorator(login_required, name='dispatch')
class GetIngredients(View):
    """
    Запрос в базу.

    Получает из request строку запроса. Выполняет поиск в базе ингредиентов
    по их названию. Возвращает JSON.
    """

    def get(self, request):
        """Метод get."""
        query = unquote(request.GET.get('query'))
        data = list(
            Product.objects.filter(title__startswith=query).values('title',
                                                                   'unit'))
        return JsonResponse(data, safe=False)


class ProfileView(View):
    """Станица с рецептами одного автора."""

    def get_queryset(self, request):
        """Запрос для страницы автора."""
        tags = request.GET.getlist('tag')
        recipes = Recipe.recipes.tag_filter(tags)
        return recipes

    def get(self, request, user_id):
        """Для станица с рецептами одного автора доступен только метод GET."""
        recipes = self.get_queryset(request)
        author = get_object_or_404(User, id=user_id)
        paginator = Paginator(recipes.filter(author=author), RECIPES_ON_PAGE)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        context = {'author': author,
                   'page': page,
                   'paginator': paginator
                   }
        return render(request, 'recipes/profile.html', context)


@require_http_methods(["GET"])
def recipe_item_view(request, recipe_id):
    """Страница с одним рецептом."""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    context = {
        'recipe': recipe,
    }
    return render(request, 'recipes/singlePage.html', context)


@login_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def recipe_edit_view(request, recipe_id):
    """Страница редактирования рецепта."""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user != recipe.author:
        return redirect('recipe_view', recipe_id=recipe_id)
    if request.method == 'POST':
        form = RecipeForm(request.POST or None, files=request.FILES or None,
                          instance=recipe)
        if form.is_valid():
            recipe.ingredients.remove()
            recipe.recipe_amount.all().delete()
            recipe = form.save(commit=False)
            recipe.author = request.user
            ingredients = form.cleaned_data['ingredients']
            form.cleaned_data['ingredients'] = []
            form.save()
            Ingredient.objects.bulk_create(
                get_ingredients_from_form(ingredients, recipe))
            return redirect('recipe_view', recipe_id=recipe_id)

    form = RecipeForm(instance=recipe)
    context = {
        'recipe_id': recipe_id,
        'page_title': 'Редактирование рецепта',
        'button': 'Сохранить',
        'form': form,
        'recipe': recipe
    }
    return render(request, 'recipes/formRecipe.html', context)


@login_required(login_url='login')
@require_http_methods(["GET"])
def recipe_delete(request, recipe_id):
    """Удаление рецепта."""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    recipe.delete()
    return redirect('index_view')


@method_decorator(login_required, name='dispatch')
class FollowersView(View):
    """Страница мои подписки."""

    def get(self, request):
        """Метод get."""
        subscriptions = Subscription.objects.filter(
            user=request.user).order_by('pk')
        page_num = request.GET.get('page')
        paginator = Paginator(subscriptions, RECIPES_ON_PAGE)
        page = paginator.get_page(page_num)
        context = {
            'active': 'subscription',
            'paginator': paginator,
            'page': page,
        }
        return render(request, 'recipes/myFollow.html', context)


@method_decorator(login_required, name='dispatch')
class SubscriptionDelete(View):
    """Отписка от подписки на автора."""

    def delete(self, request, author_id):
        """Метод delete."""
        author = get_object_or_404(User, id=author_id)
        follow = Subscription.objects.filter(user=request.user,
                                             author=author)
        quantity, obj_subscription = follow.delete()
        if quantity == 0:
            data = {'success': False}
        else:
            data = {'success': True}
        return JsonResponse(data)


@method_decorator(login_required, name='dispatch')
class FavoriteView(View):
    """Класс для страницы избранное."""

    def get(self, request):
        """Страница избранное."""
        tags = request.GET.getlist('tag')
        user = request.user
        recipes = Favorite.favorite.get_tag_filtered(user, tags)
        paginator = Paginator(recipes, RECIPES_ON_PAGE)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        context = {'title': 'Избранное',
                   'page': page,
                   'paginator': paginator
                   }
        return render(request, 'recipes/indexAuth.html', context)

    def post(self, request):
        """Добавление рецепта в избранные."""
        json_data = json.loads(request.body.decode())
        recipe_id = json_data['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        data = {'success': True}
        favorite, created = Favorite.favorite.get_or_create(user=request.user)
        is_favorite = favorite.recipes.filter(id=recipe_id).exists()
        if is_favorite:
            data['success'] = False
        else:
            favorite.recipes.add(recipe)
        return JsonResponse(data)


@method_decorator(login_required, name='dispatch')
class FavoriteDelete(View):
    """Удаление рецепта из избранного."""

    def delete(self, request, recipe_id):
        """Метод delete."""
        recipe = get_object_or_404(Recipe, id=recipe_id)
        favorite = Favorite.favorite.filter(user=request.user, recipes=recipe)
        quantity, obj_favorite = favorite.delete()
        if quantity == 0:
            data = {'success': False}
        else:
            data = {'success': True}
        return JsonResponse(data)


@method_decorator(login_required, name='dispatch')
class PurchaseView(View):
    """Страница списка покупок. Добавление рецепта в список покупок."""

    def get(self, request):
        """Метод get."""
        recipes = Purchase.purchase.get_purchases_list(request.user)
        context = {
            'recipes': recipes,
            'active': 'purchase'
        }
        return render(request, 'recipes/shopList.html', context)

    def post(self, request):
        """Добавление рецепта в список покупок."""
        json_data = json.loads(request.body.decode())
        recipe_id = json_data['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        purchase, created = Purchase.purchase.get_or_create(user=request.user)
        data = {'success': True}
        if not Purchase.purchase.filter(recipes=recipe,
                                        user=request.user).exists():
            purchase.recipes.add(recipe)
            return JsonResponse(data)

        data['success'] = False
        return JsonResponse(data)


@method_decorator(login_required, name='dispatch')
class PurchaseDelete(View):
    """Удаление рецепта из списка покупок."""

    def delete(self, request, recipe_id):
        """Метод delete."""
        recipe = get_object_or_404(Recipe, id=recipe_id)
        data = {'success': True}
        try:
            purchase = Purchase.purchase.get(user=request.user)
        except ObjectDoesNotExist:
            data['success'] = False
        if not purchase.recipes.filter(id=recipe_id).exists():
            data['success'] = False
        purchase.recipes.remove(recipe)
        return JsonResponse(data)


@method_decorator(login_required, name='dispatch')
class SendShopList(View):
    """Сохранение списка покупок."""

    def get(self, request):
        """Метод get."""
        user = request.user
        ingredients = Ingredient.objects.select_related('ingredient').filter(
            recipe__purchase__user=user).values('ingredient__title',
                                                'ingredient__unit').annotate(
            total=Sum('amount'))
        filename = '{}_list.txt'.format(user.username)
        products = []
        for ingredient in ingredients:
            products.append(
                '{} ({}) - {}'.format(ingredient["ingredient__title"],
                                      ingredient["ingredient__unit"],
                                      ingredient["total"]))
        content = 'Продукт (единицы) - количество \n \n' + '\n'.join(products)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


@method_decorator(login_required, name='dispatch')
class Subscriptions(View):
    """Добавление подписки на автора."""

    def post(self, request):
        """Метод post."""
        json_data = json.loads(request.body.decode())
        author = get_object_or_404(User, id=json_data['id'])
        is_exist = Subscription.objects.filter(
            user=request.user, author=author).exists()
        data = {'success': True}
        if is_exist:
            data['success'] = False
        else:
            Subscription.objects.create(user=request.user, author=author)
        return JsonResponse(data)


def page_not_found(request, exception):
    """Обработчик ошибки 404."""
    return render(request,
                  'recipes/misc/404.html',
                  {'path': request.path},
                  status=404)


def server_error(request):
    """Обработчик ошибки 500."""
    return render(request, 'recipes/misc/500.html', status=500)
