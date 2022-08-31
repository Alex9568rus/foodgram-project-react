from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CustomUserViewSet, IngredientsViewSet, RecipeViewSet, TagsViewSet,
    FavoriteRecipeView, ShoppingCartView
)


router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('api/auth/', include('djoser.urls.authtoken')),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/recipes/<int:id>/favorite/', FavoriteRecipeView.as_view()),
    path('api/recipes/<int:id>/shopping_cart/', ShoppingCartView.as_view())
]
