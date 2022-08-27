from django.contrib import admin
from recipes.models import (ShoppingCart, Favorite, IngredientRecipe, Ingredient,
                        Recipe, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'


class IngredientsInRecipeAdmin(admin.StackedInline):
    model = IngredientRecipe
    autocomplete_fields = ('ingredient', )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientsInRecipeAdmin, )
    list_display = ('id', 'name', 'author')
    search_fields = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name', )
    search_fields = ('name', )
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = '-пусто-'
