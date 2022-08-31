import csv
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'foodgram.settings')


import django


django.setup()


from recipes.models import Ingredient, Tag

path = './data'
os.chdir(path)


with open('ingredients.csv', encoding='utf8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        _, instance = Ingredient.objects.get_or_create(
            name=row[0],
            measurement_unit=row[1]
        )


with open('tags.csv', encoding='utf8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        _, instance = Tag.objects.get_or_create(
            name=row[0],
            color=row[1],
            slug=row[2]
        )
