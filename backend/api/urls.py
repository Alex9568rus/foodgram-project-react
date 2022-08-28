from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework.routers import DefaultRouter

from api.views import (
    TagViewSet, IngredientViewSet, RecipeViewSet,
    UserViewSet, SubscribeViewSet
)


router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    #path(
    #    'usres/<int:id>/subscribe/',
    #    SubscribeViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
    #    name='subscribe'
    #),
    #path(
    #    'users/subscriptions/', SubscribeViewSet.as_view({'get': 'list'}),
    #    name='subscriptions'
    #),
    #path(
    #    'auth/token/login/', TokenCreateView.as_view(),
    #    name='create_token'
    #),
    #path(
    #    'auth/token/logout/', TokenDestroyView.as_view(), name='delete_token'
    #),
]
