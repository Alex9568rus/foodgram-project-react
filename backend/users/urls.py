from django.urls import include, path

from users.views import CustomUserViewSet

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/subscriptions/', SubscribeViews.as_view()),
    path('users/<int:pk>/subscribe/', SubscribeViews.as_view())
]
