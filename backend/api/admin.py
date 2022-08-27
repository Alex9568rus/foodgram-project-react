from django.contrib import admin
from api.models import (Cart, FavoriteRecipe, IngredienInRecipe, Ingredient,
                        Recipe, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'


@admin.register(IngredienInRecipe)
class IngredientsInRecipeAdmin(admin.StackedInline):
    model = IngredienInRecipe
    autocomplete_fields = ('id', 'ingredient', 'recipe', 'amount')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientsInRecipeAdmin, )
    list_display = ('id', 'name', 'author', 'num_favorites')
    search_fields = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'

    def num_favorites(self, obj):
        return obj.favorites.count


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name', )
    search_fields = ('name', )
    empty_value_display = '-пусто-'


@admin.register(FavoriteRecipe)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = '-пусто-'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = '-пусто-'
