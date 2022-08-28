from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    CustomUserViewSet, IngredientViewSet, RecipeViewSet, TagViewSet
)

router = DefaultRouter()

router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('api/auth/', include('djoser.urls.authtoken')),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls))
]
