from rest_framework import status
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.pagination import Pagination
from users.models import Follow, User
from users.serializers import SubscribeListSerializer, SubscribeSerializer


class SubscribeAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = Pagination

    def post(self, request, id):
        author = get_object_or_404(User, id=id)
        user = request.user
        data = {'auhtor': author.id, 'user': user.id}
        serializer = SubscribeSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscribe = get_object_or_404(Follow, user=user, author=author)
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeListAPIView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    pagination_class = Pagination
    serializer_class = SubscribeListSerializer

    def get_queryset(self):
        user = self.request.user
        return user.follower.all()
