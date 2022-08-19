import csv
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'foodgram.settings')


import django


django.setup()


from api.models import Ingredient


path = '../data'
os.chdir(path)


with open('ingredients.csv', encoding='utf8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        _, instance = Ingredient.objects.get_or_create(
            name=row[0],
            measurement_unit=row[1]
        )
