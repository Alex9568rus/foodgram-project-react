from django.db.models.aggregates import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser import serializers
from rest_framework import status, viewsets, validators
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.mixins import ListAndRetrieveViewSet
from api.filters import IngredientFilter, RecipesByTagsFilter
from api.permissions import (
    IsAuthorOrReadOnly, IsAdminOrReadOnly, ListOrCriatePermission
)
from api.serializers import (
    CreateRecipeSerializer, IngredientSerializer, RecipeSerializer,
    TagSerializer, UserSerializer, SimpleRecipeSerializer,
    SubscribeSerializer
)
from recipes.models import (
    ShoppingCart, Favorite, Recipe, Ingredient, IngredientRecipe, Tag
)
from users.models import User, Subscribe


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (ListOrCriatePermission, )

    def perform_create(self, serializer):
        password = serializer.validated_data['password']
        user = serializer.save()
        user.set_passpord(password)
        user.save()

    #@action(detail=False, methods=['GET'])
    #def me(self, request):
    #    serializer = self.get_serializer(self.request.user)
    #    return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def set_password(self, request):
        serializer = serializers.SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(
            serializer.validated_data['new_password']
        )
        self.request.user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TagViewSet(ListAndRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = None


class IngredientViewSet(ListAndRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filterset_class = IngredientFilter
    #search_fields = ('name', )
    pagination_class = None


class SubscribeViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        queryset = User.objects.filter(
            following__user=self.request.user
        )
        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.user == author:
            raise validators.ValidationError(
                'Вы не можете подписаться на себя!'
            )
        if Subscribe.objects.filter(
            user=request.user, author=author
        ).exists():
            raise validators.ValidationError(
                'Вы уже подписаны на автора!'
            )
        Subscribe.objects.create(user=request.user, author=author)
        serializer = SubscribeSerializer(author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, id):
        author = get_object_or_404(User, id=id)
        Subscribe.objects.filter(
            user=request.user, author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly)
    filterset_class = RecipesByTagsFilter
    #search_fields = ('name', 'user')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_or_delete_recipe(self, model, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        serializer = SimpleRecipeSerializer(
            recipe, context={'request': request}
        )
        if request.method == 'POST':
            model.objects.create(
                user=request.user,
                recipe=recipe
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        model.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated, )
    )
    def favorite(self, request, id):
        return self.add_or_delete_recipe(
            Favorite, request, id
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated, )
    )
    def shopping_cart(self, request, id):
        return self.add_or_delete_recipe(
            ShoppingCart, request, id
        )

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
