import csv
import django
import os
from api.models import Ingredient

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'foodgram.settings')


django.setup()


path = '../data'
os.chdir(path)


with open('ingredients.csv', encoding='utf8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        _, instance = Ingredient.objects.get_or_create(
            name=row[0],
            measurement_unit=row[1]
        )
