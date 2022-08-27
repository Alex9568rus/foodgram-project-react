import io

from django.db.models.aggregates import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfgen import canvas
from reportlab.pdfbase import ttfonts, pdfmetrics
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.mixins import ListAndRetrieveViewSet
from api.models import (
    Cart, FavoriteRecipe, Recipe, Ingredient, IngredienInRecipe, Tag
)
from api.filters import IngredientFilter, RecipesByTagsFilter
from api.pagination import Pagination
from api.permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly
from api.serializers import (
    CartSerializer, CreateRecipeSerializer, FavoriteSerializer,
    IngredientSerializer, RecipeSerializer, TagSerializer
)
from foodgram.settings import X_POSITION, Y_POSITION, STRING_GAP, FILE_NAME
from users.serializers import SubscribeRecipeSerializer


class TagViewSet(ListAndRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly, )


class IngredientViewSet(ListAndRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filterset_class = IngredientFilter
    search_fields = ('name', )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipesByTagsFilter
    pagination_class = Pagination
    search_fields = ('name', 'user')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return CreateRecipeSerializer

    def add_or_delete_recipe(self, model, obj_serializer, request, id):
        recipe = get_object_or_404(
            model, id=id
        )
        serializer = obj_serializer(
            data={'user': request.user, 'recipe': request.recipe.id}
        )
        if request.method == 'POST':
            serializer.is_valid()
            serializer.save()
            serializer = SubscribeRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            delete_recipe = get_object_or_404(
                model, user=request.user, id=id
            )
            delete_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated, )
    )
    def favorite(self, request, id):
        return self.add_or_delete_recipe(
            FavoriteRecipe, FavoriteSerializer, request, id
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated, )
    )
    def shoping_cart(self, request, id):
        return self.add_or_delete_recipe(
            Cart, CartSerializer, request, id
        )

    @action(
        methods=['GET', ],
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        buffer = io.BytesIO()
        page = canvas.Canvas(buffer)
        pdfmetrics.registerFont(
            ttfonts.TTFont('FreeSans', 'FreeSans.ttf', 'UTF-8')
        )
        recipes = request.user.shoping_carts.all().values('recipe_id')
        shopping_list = IngredienInRecipe.objects.filter(
            recipe__in=recipes
        ).values(
            'ingredient__name', 'ingredient__measurement_unit',
        ).order_by('ingredient__name').annotate(
            amount=Sum('amount')
        )
        y_position = Y_POSITION
        if shopping_list:
            for index, recipe in enumerate(shopping_list, start=1):
                page.setFont('FreeSans', 15)
                page.drawString(
                    X_POSITION, y_position - STRING_GAP,
                    f'{index}) {recipe["ingredient__name"]}'
                    f'({recipe["ingredient__measurement_unit"]})'
                    f' - {recipe["amount"]}'
                )
                y_position -= 15
                if y_position <= 50:
                    page.showPage()
                    y_position = Y_POSITION
            page.save()
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=FILE_NAME
            )
        page.setFont('FreeSans', 25)
        page.drawString(
            X_POSITION, Y_POSITION, 'Нет покупок!'
        )
        page.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=FILE_NAME)
