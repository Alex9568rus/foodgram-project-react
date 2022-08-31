from django.contrib import admin
from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag


class IngredientRecipeInLine(admin.TabularInline):
    model = IngredientRecipe
    min_num = 1
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author')
    search_fields = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    inlines = (IngredientRecipeInLine,)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')
