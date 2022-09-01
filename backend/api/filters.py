from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe, Ingredient, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filtering(self, queryset, name, value):
        if name == 'is_favorited' and value:
            return queryset.filter(favorites__user=self.request.user)
        if name == 'is_in_shopping_cart' and value:
            return queryset.filter(cart__user=self.request.user)

    # def filter_is_favorited(self, queryset, name, value):
    #     if value and not self.request.user.is_anonymous:
    #         return queryset.filter(favorites__user=self.request.user)
    #     return queryset

    # def filter_is_in_shopping_cart(self, queryset, name, value):
    #     if value and not self.request.user.is_anonymous:
    #         return queryset.filter(cart__user=self.request.user)
    #     return queryset


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name', )
