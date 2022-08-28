from django.db.models.aggregates import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from djoser import views
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from api.exceptions import (
    SubscribeError, SubscribeYourselfError, RecipeExistingError
)
from api.mixins import ListAndRetrieveViewSet
from api.filters import IngredientFilter, RecipesByTagsFilter
from api.pagination import Pagination
from api.permissions import (
    IsAuthorOrReadOnly, IsAdminOrReadOnly
)
from api.serializers import (
    CreateRecipeSerializer, IngredientSerializer, RecipeSerializer,
    TagSerializer, FollowSerializer, SimpleRecipeSerializer
)
from recipes.models import (
    ShoppingCart, Favorite, Recipe, Ingredient, IngredientRecipe, Tag
)
from users.models import User, Follow


class CustomUserViewSet(views.UserViewSet):
    pagination_class = Pagination

    @action(
        detail=True, methods=['POST', ], permission_classes=(IsAuthenticated,)
    )
    def create_subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            raise SubscribeYourselfError('Нельзя подписаться на себя!')
        if Follow.objects.filter(user=user, author=author).exists():
            raise SubscribeError('Вы уже подписаны на данного автора!')
        follow = Follow.objects.create(user=user, author=author)
        serializer = FollowSerializer(follow, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @create_subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            raise SubscribeYourselfError('Нельзя отписаться от себя!')
        follow = Follow.objects.create(user=user, author=author)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise SubscribeError('Вы не подписаны данного автора!')

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ListAndRetrieveViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ListAndRetrieveViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReadOnly, )
    serializer_class = IngredientSerializer
    filter_backends = [IngredientFilter, ]
    search_fields = ('^name', )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = Pagination
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly)
    filter_backends = [DjangoFilterBackend, ]
    filter_class = RecipesByTagsFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return CreateRecipeSerializer

    def adding(self, model, user, id):
        if model.objects.filter(user=user, recipe__id=id).exists():
            raise RecipeExistingError('Рецепт уже добавлен')
        recipe = get_object_or_404(Recipe, id=id)
        model.objects.create(user=user, recipe=recipe)
        serializer = SimpleRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def deleting(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, id):
        if request.method == 'POST':
            return self.adding(Favorite, request.user, id)
        elif request.method == 'DELETE':
            return self.deleting(Favorite, request.user, id)

    @action(detail=True, methods=['POST', 'delete'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, id):
        if request.method == 'POST':
            return self.adding(ShoppingCart, request.user, id)
        elif request.method == 'DELETE':
            return self.deleting(ShoppingCart, request.user, id)

    @action(
        methods=['GET', ],
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        lines = []
        for field in IngredientRecipe.objects.filter(
            recipe__cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')):
            lines.append(
                f'* {field["ingredient__name"]}'
                f'{field["ingredient__measurement_unit"]}'
                f' - {field["amount"]}'
            )
        shopping_list = '\n'.join(lines)
        response = HttpResponse(
            shopping_list, content_type='application/pdf'
        )
        response['Content-Disposition'] = (
            'attacment; filename="ingredients_in_cart.pdf"'
        )
        return response
