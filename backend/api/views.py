from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from api.exceptions import (
    SubscribeError, SubscribeYourselfError, RecipeExistingError
)
from recipes.models import (
    Favorite, Ingredient, Recipe, ShoppingCart, Tag, IngredientRecipe
)
from api.filters import IngredientFilter, RecipeFilter
from api.pagination import Pagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (
    CreateUpdateRecipeSerializer, FollowSerializer, IngredientSerializer,
    ListRecipeSerializer, ShortRecipeSerializer, TagSerializer
)
from users.models import Follow, User


class CustomUserViewSet(UserViewSet):
    pagination_class = Pagination

    @action(detail=True,
            methods=('post',),
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            raise SubscribeYourselfError('Нельзя подписаться на себя')
        if Follow.objects.filter(user=user, author=author).exists():
            raise SubscribeError('Вы уже подписаны на данного автора')
        follow = Follow.objects.create(user=user, author=author)
        serializer = FollowSerializer(
            follow, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def del_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            raise SubscribeYourselfError('Нельзя отписаться от себя')
        follow = Follow.objects.filter(user=user, author=author)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise SubscribeError('Вы не подписаны на данного автора')

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    pagination_class = None
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return ListRecipeSerializer
        return CreateUpdateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True, methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, id=None):
        if request.method == 'POST':
            return self.add_obj(Favorite, request.user, id)
        elif request.method == 'DELETE':
            return self.delete_obj(Favorite, request.user, id)

    @action(
        detail=True, methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, id=None):
        if request.method == 'POST':
            return self.add_obj(ShoppingCart, request.user, id)
        elif request.method == 'DELETE':
            return self.delete_obj(ShoppingCart, request.user, id)

    def add_obj(self, model, user, id):
        if model.objects.filter(user=user, recipe__id=id).exists():
            raise RecipeExistingError('Рецепт уже добавлен')
        recipe = get_object_or_404(Recipe, id=id)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_obj(self, model, user, id):
        obj = model.objects.filter(user=user, recipe__id=id)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_list = '\n'.join(
                f'* {ingredient["ingredient__name"]}'
                f'{ingredient["ingredient__measurement_unit"]}'
                f' - {ingredient["amount"]}'
                for ingredient in ingredients
        )
        response = HttpResponse(
            shopping_list, content_type='application/pdf'
        )
        response['Content-Disposition'] = (
            'attacment; filename="ingredients_in_cart.pdf"'
        )
        return response
