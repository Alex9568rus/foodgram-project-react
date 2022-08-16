from django_filters.rest_framework import filters, FilterSet
from api.models import Ingredient, Recipe
from users.models import User


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='startwith')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipesByTagsFilter(FilterSet):
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
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
            'tags', 'author', 'is_favorited', 'is_in_shoping_cart'
        )

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def get_is_in_shoping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shoping_cart__user=self.request.user)
        return queryset
