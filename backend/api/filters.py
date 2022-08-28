from django_filters.rest_framework import filters, FilterSet
from recipes.models import Recipe, Ingredient


class IngredientFilter(FilterSet):
    name = filters.CharFilter(
        field_name='name', lookup_expr='istartwith'
    )

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipesByTagsFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = filters.CharFilter(
        method='filter_is_favorited'
    )
    is_in_shoping_cart = filters.CharFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags', 'author', 'is_favorited', 'is_in_shopping_cart'
        )

    def filter_is_favorited(self, queryset, is_favorited, slug):
        if self.request.user.is_authenticated:
            return queryset
        if self.request.query_params.get('is_favorited'):
            return queryset.filter(
                favorite__user=self.request.user
            ).distinct()
        return queryset

    def filter_is_in_shopping_cart(self, queryset, is_in_shopping_cart, slug):
        if self.request.user.is_authenticated:
            return queryset
        if self.request.query_params.get('is_in_shoping_cart'):
            return queryset.filter(
                cart__user=self.request.user
            ).distinct()
        return queryset
