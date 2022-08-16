from django.urls import path, include
from users.views import SubscribeAPIView, SubscribeListAPIView


urlpatterns = [
    path('users/<int:id>/subscribe/', SubscribeAPIView.as_view()),
    path('users/subscriptions/', SubscribeListAPIView.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
