"""Тесты view приложения Recipes."""
import csv

from django.test import Client, TestCase
from django.urls import reverse

import factory

from users.models import Subscription

from recipes.models import Favorite, \
    Ingredient, Product, Purchase, Recipe, Tag, User


def _create_recipe(author, name, tag):
    products = [Product.objects.create(
        title=f'testIng{i}', unit=i) for i in range(2)]
    recipe = Recipe(author=author, name=name,
                    description='test test test', cook_time=5)
    recipe.save()
    recipe.tags.add(tag)
    for product in products:
        ingredient = Ingredient(
            recipe=recipe, ingredient=product, amount=2)
        ingredient.save()
    return recipe


class UserFactory(factory.Factory):
    """
    Класс Factory.

    Класс для создания пользователей через библиотеку Factory Boy.
    """

    class Meta:
        """Модель экземпляры которой создаем."""

        model = User

    username = 'Test user'
    email = 'test@test.test'
    password = '12345six'
    first_name = 'Test user first_name'


def _create_user(**kwargs):
    """Создаем пользователя."""
    user = UserFactory.create(**kwargs)
    user.save()
    return user


class TestPageHeader(TestCase):
    """
    Тесты для шапки страницы.

    Для неавторизованного пользователя проверяет, что в шапке страницы есть
    меню для авторизации и нет для создания рецепта.
    Для авторизованного пользователя проверяет, что в шапке нет пункта
    авторизации, но есть для изменения пароля, появился пункт создания рецепта
    и счетчик количества рецептов в списке покупок.
    """

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()
        self.user = _create_user()

    def test_not_auth_user(self):
        """Тест не авторизированного пользователя."""
        response = self.client.get(reverse('index_view'))
        self.assertEqual(
            response.status_code, 200,
            msg='Главная страница должна быть доступна')
        html = f'<a href="{reverse("login")}" class="nav__link link">Войти'
        self.assertIn(
            html, response.content.decode(),
            msg='У неавторизованного юзера в шапке должен быть пункт Войти')
        html = f'<a href="{reverse("recipe_new_view")}"' \
               f' class="nav__link link">Создать рецепт'
        self.assertNotIn(
            html, response.content.decode(),
            msg=('У неавторизованного юзера в шапке не должно быть'
                 ' пункта Создать рецепт'))

    def test_auth_user(self):
        """Тест авторизированного пользователя."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('index_view'))
        html = f'<a href="{reverse("login")}" class="nav__link link">Войти'
        self.assertNotIn(
            html, response.content.decode(),
            msg='У авторизованного юзера в шапке не должно быть пункта Войти')
        html = 'class="nav__link link">Изменить пароль'
        self.assertIn(
            html, response.content.decode(),
            msg='У залогиненного юзера в шапке должен быть пункт смены пароля')
        html = f'<a href="{reverse("recipe_new_view")}"' \
               f' class="nav__link link">Создать рецепт'
        self.assertIn(
            html, response.content.decode(),
            msg=('У залогиненного юзера в шапке должен быть пункт'
                 ' Создать рецепт'))
        counter = 'nav__badge" id="counter">'
        self.assertIn(
            counter, response.content.decode(),
            msg='У авторизованного юзера в шапке должен быть счетчик покупок')


class TestTagFilter(TestCase):
    """
    Тесты для фильтрации по тегам.

    Проверяет работу фильтров по тегам на главной странице,
    странице профиля и избранного.
    """

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()
        self.user = _create_user()
        self.client.force_login(self.user)
        tag1 = Tag.objects.create(name='завтрак', slug='breakfast',
                                  colors='orange')
        tag2 = Tag.objects.create(name='обед', slug='lunch', colors='green')
        for i in range(15):
            if i % 2 == 0:
                _create_recipe(self.user, f'recipe {i}', tag2)
            else:
                _create_recipe(self.user, f'recipe {i}', tag1)

    def test_filter(self):
        """Тест фильтров."""
        urls = [
            f'{reverse("index_view")}?tag=lunch',
            f'{reverse("index_view")}?tag=lunch&page=2',
            f'{reverse("profile_view", args=[self.user.id])}?tag=lunch',
            f'{reverse("profile_view", args=[self.user.id])}?tag=lunch&page=2',
        ]
        tag = 'card__item"><span class="badge badge_style_orange">завтрак'
        for url in urls:
            resp = self.client.get(url)
            self.assertNotIn(
                tag, resp.content.decode(),
                msg=('Фильтры по тегам должны работать правильно на'
                     f'{resp.request["PATH_INFO"]}, а также при пагинации'))
        self.client.force_login(self.user)
        for i in range(1, 3):
            self.client.post(
                reverse('favorite_view'), data={'id': f'{i}'},
                content_type='application/json')
        resp = self.client.get(f'{reverse("favorite_view")}?tag=lunch')
        self.assertNotIn(
            tag, resp.content.decode(),
            msg='Фильтры должны правильно работать на странице с избранным')


class TestProfilePage(TestCase):
    """
    Тесты для страницы профиля.

    Для неавторизованного пользователя проверяет, что страница доступна и на
    ней нет кнопки подписки.
    Для авторизованного пользователя проверяет, что в своем профиле нет кнопки
    подписке, а на чужом есть.
    """

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()
        self.user = _create_user()
        self.user2 = _create_user(username='Another test user',
                                  email='another@test.test',
                                  password='onetwo34',
                                  first_name='Another test user first_name')

    def test_not_auth_user(self):
        """Тест не авторизированного пользователя."""
        response = self.client.get(
            reverse('profile_view', args=[self.user.id]))
        self.assertEqual(
            response.status_code, 200,
            msg='Неавторизованный юзер может просматривать профиль автора')
        subscribe_btn = '"light-blue button_size_auto" name="subscribe"'
        self.assertNotIn(
            subscribe_btn, response.content.decode(),
            msg=('В профиле для незалогиненного юзера не должно быть'
                 ' кнопки подписки'))

    def test_auth_user(self):
        """Тест авторизированного пользователя."""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('profile_view', args=[self.user.id]))
        self.assertEqual(
            response.status_code, 200,
            msg='Авторизованный пользователь может просматривать свой профиль')
        subscribe_btn = 'name="subscribe"'
        self.assertNotIn(
            subscribe_btn, response.content.decode(),
            msg=('В своем профиле для авторизованного юзера не должно'
                 ' быть кнопки подписки'))
        response2 = self.client.get(
            reverse('profile_view', args=[self.user2.id]))

        self.assertIn(
            subscribe_btn, response2.content.decode(),
            msg=('Для авторизованного юзера в профиле другого юзера должна'
                 ' быть кнопка подписки'))


class TestRecipePage(TestCase):
    """
    Тесты страницы отдельного рецепта.

    Для неавторизованного пользователя проверяет, что страница доступна; на
    странице отсутствуют кнопки добавления в избранное, список покупок и
    подписки.
    Для авторизованного пользователя проверяет, что на странице появляются
    кнопки добавления в ибранное и список покупок; на странице своего рецепта
    есть кнопка редактирования и нет кнопки добавления в подписки, а на
    странице чужого рецепта появляется кнопка подписки.
    """

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()
        self.user = _create_user()
        self.user2 = _create_user(username='Another test user',
                                  email='another@test.test',
                                  password='onetwo34',
                                  first_name='Another test user first_name')
        tag = Tag.objects.create(name='завтрак', slug='breakfast')
        self.recipe = _create_recipe(self.user, 'Test recipe', tag)
        self.recipe2 = _create_recipe(self.user2, 'Another recipe', tag)

    def test_not_auth_user(self):
        """Тест не авторизированного пользователя."""
        response = self.client.get(
            reverse('recipe_view', args=[self.recipe.id]))
        self.assertEqual(
            response.status_code, 200,
            msg=('Страница отдельного рецепта должна быть доступна'
                 ' неавторизованному юзеру'))
        elements = [
            ['избранное', 'button_style_none" name="favorites"'],
            ['подписки', 'light-blue button_size_auto" name="subscribe"'],
            ['покупок', 'button_style_blue" name="purchases"']
        ]
        for button, element in elements:
            self.assertNotIn(
                element,
                response.content.decode(),
                msg=(f'Кнопка {button} не должна быть на странице для '
                     'неавторизованного пользователя'))

    def test_auth_user(self):
        """Тест авторизированного пользователя."""
        self.client.force_login(self.user)
        response1 = self.client.get(
            reverse('recipe_view', args=[self.recipe.id]))
        self.assertEqual(
            response1.status_code, 200,
            msg=('Страница отдельного рецепта должна быть доступна'
                 ' авторизованному юзеру'))
        elements = [
            ['избранное', 'name="favorites"'],
            ['список покупок', 'name="purchases"']
        ]
        for button, element in elements:
            self.assertIn(
                element, response1.content.decode(),
                msg=(f'Кнопка {button} должна быть на странице для'
                     ' залогиненного юзера'))
        subscibe_btn = 'name="subscribe"'
        self.assertNotIn(
            subscibe_btn, response1.content.decode(),
            msg='На странице своего рецепта не должна быть кнопка подписки')
        self.assertIn(
            'Редактировать рецепт', response1.content.decode(),
            msg='На странице своего рецепта должна быть кнопка редактировать'),
        elements.append(['подписка на автора', 'name="subscribe"'])

        """Запрос на страницу чужого рецепта"""

        response2 = self.client.get(
            reverse('recipe_view', args=[self.recipe2.id]))
        self.assertEqual(
            response2.status_code, 200,
            msg='Страница чужого рецепта доступна авторизованному юзеру')
        for button, element in elements:
            self.assertIn(element, response2.content.decode(), msg=(
                f'Кнопка {button} должна быть на '
                f'странице для залогиненного юзера'))
        self.assertNotIn(
            'Редактировать рецепт', response2.content.decode(),
            msg=('Кнопка редактирования не должна быть на странице'
                 ' чужого рецепта'))


class TestFavoritePage(TestCase):
    """
    Тесты страницы избранного.

    Для неавторизованного пользователя проверяет, что страница недоступна и
    пользователь перенаправляется на страницу входа.
    Для авторизованного пользователя проверяется, что страница доступна и что
    на странице присутствует рецепт добавленный в избранное
    """

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()
        self.user = _create_user()
        tag = Tag.objects.create(name='завтрак', slug='breakfast')
        self.recipe = _create_recipe(self.user, 'Favorite recipe', tag)
        _create_recipe(self.user, 'Unfavorite recipe', tag)
        favorite = Favorite(user=self.user)
        favorite.save()
        favorite.recipes.add(Recipe.recipes.get(id=1))

    def test_not_auth_user(self):
        """Тест не авторизированного пользователя."""
        response = self.client.get(reverse('favorite_view'), follow=True)
        redirect_url = f'{reverse("login")}?next={reverse("favorite_view")}'
        self.assertRedirects(
            response,
            redirect_url,
            msg_prefix='GET-запрос на страницу избранного для '
                       'неавторизованного юзера должно перенаправлять на '
                       'страницу входа')

    def test_auth_user(self):
        """Тест авторизированного пользователя."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('favorite_view'), follow=True)
        self.assertEqual(
            response.status_code, 200,
            msg='Авторизованный юзер может зайти на страницу избранного')
        self.assertIn(
            'Favorite recipe', response.content.decode(),
            msg='На странице избранного должен быть добавленный рецепт')
        self.assertNotIn(
            'Unfavorite recipe', response.content.decode(),
            msg=('На странице избранного не должно быть рецепта,'
                 ' не добавленного в избранное'))


class TestSubscriptionPage(TestCase):
    """
    Тесты страницы подписок.

    Для неавторизованного пользователя проверяет, что страница недоступна и
    пользователь перенаправляется на страницу входа.
    Для авторизованного пользователя проверяется, что страница доступна и что
    на странице присутствует автор добавленный в подписки.
    """

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()
        self.user = _create_user()
        self.user2 = _create_user(username='Another test user',
                                  email='another@test.test',
                                  password='onetwo34',
                                  first_name='Another test user first_name')
        tag = Tag.objects.create(name='завтрак', slug='breakfast')
        self.recipe = _create_recipe(self.user, 'Test recipe', tag)
        Subscription.objects.create(user=self.user2, author=self.user)

    def test_not_auth_user(self):
        """Тест не авторизированного пользователя."""
        response = self.client.get(reverse('subscriptions'), follow=True)
        redirect_url = f'{reverse("login")}?next={reverse("subscriptions")}'
        self.assertRedirects(
            response,
            redirect_url,
            msg_prefix='GET-запрос на страницу подписок неавторизованного'
                       ' юзера должно перенаправлять на страницу входа')

    def test_auth_user(self):
        """Тест авторизированного пользователя."""
        self.client.force_login(self.user2)
        response = self.client.get(reverse('followers_view'), follow=True)
        self.assertEqual(
            response.status_code, 200,
            msg='Страница подписок доступна авторизованному юзеру')
        self.assertIn(
            'Test user first_name', response.content.decode(),
            msg='На странице подписок должен быть добавленный автор')


class TestPurchasePage(TestCase):
    """
    Тесты страницы покупок.

    Для неавторизованного пользователя проверяет, что страница недоступна и
    пользователь перенаправляется на страницу входа.
    Для авторизованного пользователя проверяется, что страница доступна и что
    на странице присутствует рецепт добавленный в покупки.
    """

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()
        self.user = _create_user()
        tag = Tag.objects.create(name='завтрак', slug='breakfast')
        self.recipe = _create_recipe(self.user, 'Cool recipe', tag)
        purchase = Purchase(user=self.user)
        purchase.save()
        purchase.recipes.add(self.recipe)

    def test_not_auth_user(self):
        """Тест не авторизированного пользователя."""
        response = self.client.get(reverse('purchases_view'), follow=True)
        redirect_url = f'{reverse("login")}?next={reverse("purchases_view")}'
        self.assertRedirects(
            response,
            redirect_url,
            msg_prefix='GET-запрос на страницу покупок должен '
                       'неавторизованного юзера должно перенаправлять на '
                       'страницу входа')

    def test_auth_user(self):
        """Тест авторизированного пользователя."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('purchases_view'), follow=True)
        self.assertEqual(
            response.status_code, 200,
            msg='Страница покупок должна быть доступна авторизованному юзеру')
        self.assertIn(
            'Cool recipe', response.content.decode(),
            msg='На странице покупок должен быть добавленный рецепт')


class TestIngredientQuery(TestCase):
    """
    Тесты запросов ингридиентов.

    Для неавторизованного пользователя проверяет, что страница недоступна и
    пользователь перенаправляется на страницу входа.
    Для авторизованного пользователя проверяется, что страница доступна и что
    возвращается ответ в правильном формате JSON.
    """

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()
        self.user = _create_user()
        with open('recipes/fixtures/ingredients.csv') as isfile:
            reader = csv.reader(isfile)
            for row in reader:
                title, unit = row
                Product.objects.get_or_create(title=title, unit=unit)

    def test_not_auth_user(self):
        """Тест не авторизированного пользователя."""
        response = self.client.get(f'{reverse("ingredients")}?query=хл',
                                   follow=True)
        redirect_url = f'{reverse("login")}?next={reverse("ingredients")}' \
                       f'%3Fquery%3D%25C3%2591%25C2%2585%25C3%2590%25C2%25BB'
        self.assertRedirects(response, redirect_url,
                             msg_prefix='GET-запрос ингредиента должен '
                                        'неавторизованного юзера должно '
                                        'перенаправлять на страницу входа')

    def test_auth_user(self):
        """Тест авторизированного пользователя."""
        self.client.force_login(self.user)
        query = 'чай'
        response = self.client.get(f'{reverse("ingredients")}?query={query}',
                                   format='json')
        data = response.json()
        self.assertIsInstance(
            data, list, msg='Пришедшие данные должны иметь тип list')
        self.assertIsInstance(
            data[0], dict, msg='Элементы списка должны иметь тип dict')
        self.assertIn(
            'title', data[0],
            msg='Словарь должен содержать ключ "title"')
        self.assertIn(
            'unit', data[0],
            msg='Словарь должен содержать ключ "unit"')
        for d in data:
            self.assertTrue(
                d['title'].startswith('чай'),
                msg=f'Имя ингредиента должно начинаеться на {query}')


class TestFavoriteButton(TestCase):
    """
    Тесты страницы избранное.

    Для неавторизованного пользователя проверяет, что страница недоступна и
    пользователь перенаправляется на страницу входа.
    Для авторизованного пользователя проверяется, что страница доступна и что
    добавление и удаление рецепта происходит корректно.
    """

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()
        self.user = _create_user()
        tag = Tag.objects.create(name='завтрак', slug='breakfast')
        self.recipe = _create_recipe(self.user, 'Cool recipe', tag)
        self.data = {'id': f'{self.recipe.id}'}

    def test_not_auth_user(self):
        """Тест не авторизированного пользователя."""
        response = self.client.post(
            reverse('favorite_view'), data=self.data,
            content_type='application/json', follow=True)
        redirect_url = f'{reverse("login")}?next={reverse("favorite_view")}'
        self.assertRedirects(response, redirect_url,
                             msg_prefix='Запрос на добавление в избранное '
                                        'должен неавторизованного юзера должно'
                                        ' перенаправлять на страницу входа')

        response = self.client.delete(
            reverse('favorite_delete', args=[self.recipe.id]),
            content_type='application/json', follow=True)
        redirect_url = f'{reverse("login")}?next=' \
                       f'{reverse("favorite_delete", args=[self.recipe.id])}'
        self.assertRedirects(response, redirect_url,
                             msg_prefix='Запрос на удаление из избранного '
                                        'должен неавторизованного юзера должно'
                                        ' перенаправлять на страницу входа')

    def test_auth_user_add(self):
        """Тест авторизированного пользователя. Добавление."""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('favorite_view'), data=self.data,
            content_type='application/json', follow=True)
        data_incoming = response.json()
        self.assertIsInstance(data_incoming, dict,
                              msg='На запрос должен приходить словарь')
        self.assertIn('success', data_incoming,
                      msg='Словарь должен содержать ключ "success"')
        self.assertEqual(data_incoming['success'], True,
                         msg='При добавлении в избранное success = True')
        self.assertTrue(Favorite.favorite.get(
            user=self.user).recipes.filter(id=self.recipe.id).exists(),
                        msg='Должна создаваться соответствующая запись в бд')
        repeat_response = self.client.post(
            reverse('favorite_view'), data=self.data,
            content_type='application/json', follow=True)
        data_incoming_2 = repeat_response.json()
        self.assertEqual(
            data_incoming_2['success'], False,
            msg='При попытке повторно добавить в избранное success = False')
        self.assertEqual(Favorite.favorite.get(
            user=self.user).recipes.filter(id=self.recipe.id).count(), 1,
                         msg='Не должна создаваться повторная запись в бд')

    def test_auth_user_delete(self):
        """Тест авторизированного пользователя. Удаление."""
        self.client.force_login(self.user)
        self.client.post(
            reverse('favorite_view'), data=self.data,
            content_type='application/json', follow=True)
        del_response = self.client.delete(
            reverse('favorite_delete', args=[self.recipe.id]),
            content_type='application/json', follow=True)
        data_incoming = del_response.json()
        self.assertIsInstance(data_incoming, dict,
                              msg='На запрос должен приходить словарь')
        self.assertIn('success', data_incoming,
                      msg='Словарь должен содержать ключ "success"')
        self.assertEqual(data_incoming['success'], True,
                         msg='При удалении из избранного success = True')
        self.assertFalse(Favorite.favorite.filter(recipes=self.recipe,
                                                  user=self.user)
                         .exists(),
                         msg='Должна удаляться соответствующая запись в бд')
        repeat_del_response = self.client.delete(
            reverse('favorite_delete', args=[self.recipe.id]),
            content_type='application/json', follow=True)
        data_incoming_2 = repeat_del_response.json()
        self.assertEqual(
            data_incoming_2['success'], False,
            msg='При попытке повторно удалить из избранного success = False')


class TestSubscriptionButton(TestCase):
    """
    Тесты страницы мои подписки.

    Для неавторизованного пользователя проверяет, что страница недоступна и
    пользователь перенаправляется на страницу входа.
    Для авторизованного пользователя проверяется, что страница доступна и что
    добовление и удаление подписки на автора происходит корректно.
    """

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()
        self.user = _create_user()
        self.user2 = _create_user(username='Another test user',
                                  email='another@test.test',
                                  password='onetwo34',
                                  first_name='Another test user first_name')
        self.data = {'id': f'{self.user2.id}'}

    def test_not_auth_user(self):
        """Тест не авторизированного пользователя."""
        response = self.client.post(
            reverse('subscriptions'), data=self.data,
            content_type='application/json', follow=True)
        redirect_url = f'{reverse("login")}?next={reverse("subscriptions")}'
        self.assertRedirects(response, redirect_url,
                             msg_prefix='Запрос на добавление в подписки '
                                        'должно неавторизованного юзера должно'
                                        ' перенаправлять на страницу входа')

        response = self.client.delete(
            reverse('subscription_delete', args=[self.user2.id]),
            content_type='application/json', follow=True)
        redirect_url = f'{reverse("login")}?next=' \
                       f'{reverse("subscription_delete", args=[self.user2.id])}'
        self.assertRedirects(response, redirect_url,
                             msg_prefix='Запрос на удаление из подписки должен'
                                        ' неавторизованного юзера должно '
                                        'перенаправлять на страницу входа')

    def test_auth_user_add(self):
        """Тест авторизированного пользователя. Добавление."""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('subscriptions'), data=self.data,
            content_type='application/json', follow=True)
        data_incoming = response.json()
        self.assertIsInstance(data_incoming, dict,
                              msg='Проверьте, что на запрос приходит словарь')
        self.assertIn('success', data_incoming,
                      msg='Проверьте, что словарь содержит ключ "success"')
        self.assertEqual(data_incoming['success'], True,
                         msg='При добавлении в подписки значение ключа = True')
        self.assertTrue(Subscription.objects.filter(
            user=self.user, author=self.user2).exists(),
                        msg='Должна создаваться соответствующая запись в бд')
        repeat_response = self.client.post(
            reverse('subscriptions'), data=self.data,
            content_type='application/json', follow=True)
        data_incoming_2 = repeat_response.json()
        self.assertEqual(
            data_incoming_2['success'], False,
            msg='При попытке повторно добавить в подписки success = False')
        self.assertEqual(Subscription.objects.filter(
            user=self.user, author=self.user2).count(), 1,
                         msg='Не должна создаваться повторная запись в бд')

    def test_auth_user_delete(self):
        """Тест авторизированного пользователя. Удаление."""
        self.client.force_login(self.user)
        self.client.post(
            reverse('subscriptions'), data=self.data,
            content_type='application/json', follow=True)
        del_response = self.client.delete(
            reverse('subscription_delete', args=[self.user2.id]),
            content_type='application/json', follow=True)
        data_incoming = del_response.json()
        self.assertIsInstance(data_incoming, dict,
                              msg='На запрос должен приходить словарь')
        self.assertIn('success', data_incoming,
                      msg='Словарь должен содержать ключ "success"')
        self.assertEqual(data_incoming['success'], True,
                         msg='При удалении из подписок значение ключа = True')
        self.assertFalse(Subscription.objects.filter(
            user=self.user, author=self.user2).exists(),
                         msg='Должна удаляться соответствующая запись в бд')
        repeat_del_response = self.client.delete(
            reverse('subscription_delete', args=[self.user2.id]),
            content_type='application/json', follow=True)
        data_incoming_2 = repeat_del_response.json()
        self.assertEqual(
            data_incoming_2['success'], False,
            msg='При попытке повторно удалить из подписок success = False')


class TestPurchaseButton(TestCase):
    """
    Тесты страницы список покупок.

    Для неавторизованного пользователя проверяет, что страница недоступна и
    пользователь перенаправляется на страницу входа.
    Для авторизованного пользователя проверяется, что страница доступна и что
    добовление и удаление рецепта в список покупок происходит корректно.
    """

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()
        self.user = _create_user()
        tag = Tag.objects.create(name='завтрак', slug='breakfast')
        self.recipe = _create_recipe(self.user, 'Cool recipe', tag)
        self.data = {'id': f'{self.recipe.id}'}

    def test_not_auth_user(self):
        """Тест не авторизированного пользователя."""
        response = self.client.post(
            reverse('purchases_view'), data=self.data,
            content_type='application/json', follow=True)
        redirect_url = f'{reverse("login")}?next={reverse("purchases_view")}'
        self.assertRedirects(response, redirect_url,
                             msg_prefix='Запрос на добавление в покупки должен'
                                        ' неавторизованного юзера должно '
                                        'перенаправлять на страницу входа')

        response = self.client.delete(
            reverse('purchase_delete', args=[self.recipe.id]),
            content_type='application/json', follow=True)
        redirect_url = f'{reverse("login")}?next=' \
                       f'{reverse("purchase_delete", args=[self.recipe.id])}'
        self.assertRedirects(response, redirect_url,
                             msg_prefix=(
                                 'Запросе на удаление из покупок должен '
                                 'неавторизованного юзера направлять на '
                                 'страницу входа'))

    def test_auth_user_add(self):
        """Тест авторизированного пользователя. Добавление."""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('purchases_view'), data=self.data,
            content_type='application/json', follow=True)
        data_incoming = response.json()
        self.assertIsInstance(data_incoming, dict,
                              msg='На запрос должен приходить словарь')
        self.assertIn('success', data_incoming,
                      msg='Словарь должен содержать ключ "success"')
        self.assertEqual(data_incoming['success'], True,
                         msg='При добавлении в покупки значение ключа = True')
        self.assertTrue(Purchase.purchase.filter(user=self.user).exists(),
                        msg='Должна создаваться соответствующая запись в бд')
        repeat_response = self.client.post(
            reverse('purchases_view'), data=self.data,
            content_type='application/json', follow=True)
        data_incoming_2 = repeat_response.json()
        self.assertEqual(
            data_incoming_2['success'], False,
            msg='При попытке повторно добавить в покупки success = False')
        self.assertEqual(Purchase.purchase.get(user=self.user).recipes.filter(
            id=self.recipe.id).count(), 1,
                         msg='Не должна создаваться повторная запись в бд')

    def test_auth_user_delete(self):
        """Тест авторизированного пользователя. Удаление."""
        self.client.force_login(self.user)
        self.client.post(reverse('purchases_view'), data=self.data,
                         content_type='application/json', follow=True)
        del_response = self.client.delete(
            reverse('purchase_delete', args=[self.recipe.id]),
            content_type='application/json', follow=True)
        data_incoming = del_response.json()
        self.assertIsInstance(data_incoming, dict,
                              msg='На запрос должен приходить словарь')
        self.assertIn('success', data_incoming,
                      msg='Словарь должен содержать ключ "success"')
        self.assertEqual(data_incoming['success'], True,
                         msg='При удалении из покупок значение ключа = True')
        self.assertFalse(Purchase.purchase.filter(recipes=self.recipe,
                                                  user=self.user)
                         .exists(),
                         msg='Должна удаляться соответствующая запись в бд')
        repeat_del_response = self.client.delete(
            reverse('purchase_delete', args=[self.recipe.id]),
            content_type='application/json', follow=True)
        data_incoming_2 = repeat_del_response.json()
        self.assertEqual(
            data_incoming_2['success'], False,
            msg='При попытке повторно удалить из покупок success = False')
