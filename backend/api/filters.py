from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe, Ingredient, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(
        method='filtering', field_name='is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filtering', field_name='is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filtering(self, queryset, name, value):
        if name == 'is_favorited' and value:
            return queryset.filter(favorites__user=self.request.user)
        if name == 'is_in_shopping_cart' and value:
            return queryset.filter(cart__user=self.request.user)


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name', )
