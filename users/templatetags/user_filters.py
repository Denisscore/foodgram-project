from django import template

from foodgram.settings import VERSION
from recipes.models import Favorite, Purchase, Tag
from users.models import Subscription

register = template.Library()


@register.filter
def url_with_get(request, page):
    query = request.GET.copy()
    query['page'] = page
    return query.urlencode()


@register.filter
def add_color(tag):
    colors = {entry['slug']: entry['colors'] for entry in
              Tag.objects.values('slug', 'colors')}
    return colors[tag.slug]


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter
def subtract(number_1, number_2):
    return int(number_1) - int(number_2)


@register.filter
def get_tags(request):
    return request.getlist('tag')


@register.filter
def renew_tag_link(request, tag):
    request_copy = request.GET.copy()
    request_copy['page'] = '1'
    tags = request_copy.getlist('tag')
    if tag.slug in tags:
        tags.remove(tag.slug)
        request_copy.setlist('tag', tags)
    else:
        request_copy.appendlist('tag', tag.slug)
    return request_copy.urlencode()


@register.filter
def is_favorite(recipe, user):
    return Favorite.favorite.filter(recipes=recipe, user=user).exists()


@register.filter
def is_purchase(recipe, user):
    return Purchase.purchase.filter(recipes=recipe, user=user).exists()


@register.filter
def is_subscribe(author, user):
    return Subscription.objects.filter(author=author, user=user).exists()


@register.filter
def all_tags(value):
    return Tag.objects.all()


@register.filter
def ingredient_count(user):
    return Purchase.purchase.counter(user)


@register.filter
def version(value):
    return VERSION
