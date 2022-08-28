from django_filters.rest_framework import filters, FilterSet
from recipes.models import Recipe, Ingredient


class IngredientFilter(FilterSet):
    name = filters.CharFilter(
        field_name='name', lookup_expr='startwith'
    )

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipesByTagsFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags', 'author', 'is_favorited', 'is_in_shopping_cart'
        )

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shoping_cart__user=self.request.user)
        return queryset
