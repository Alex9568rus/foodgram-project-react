from django_filters.rest_framework import filters, FilterSet
from api.models import Ingredient, Recipe
from users.models import User


class IngredientFilter(FilterSet):
    search_param = 'name'


class RecipesByTagsFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shoping_cart = filters.BooleanFilter(
        method='get_is_in_shoping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags', 'author'
        )

    def get_is_favorited(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def get_is_in_shoping_cart(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(shoping_cart__user=self.request.user)
        return queryset
