import csv

from django.core.management.base import BaseCommand

from recipes.models import Product, Tag


class Command(BaseCommand):
    help = 'Load product data to database'

    def handle(self, *args, **options):
        with open('recipes/fixtures/ingredients.csv', encoding='utf-8') as isfile:
            reader = csv.reader(isfile)
            for row in reader:
                title, unit = row
                Product.objects.get_or_create(title=title, unit=unit)
        Tag.objects.get_or_create(name='завтрак', slug='breakfast',
                                  colors='orange')
        Tag.objects.get_or_create(name='обед', slug='lunch', colors='green')
        Tag.objects.get_or_create(name='ужин', slug='dinner', colors='purple')
