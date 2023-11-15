from djoser.views import UserViewSet as DjoserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.pagination import RecipesUsersPagination
from .models import Subscribe, User
from .serializers import (SubscribeCreateDeleteSerializer, SubscribeSerializer,
                          UserSerializer)


class UserViewSet(DjoserViewSet):
    """Вьюсет для регистрации, смены пароля, получения списков пользователей и
    подписок, создания/удаления подписки.
    """

    UNSUBSCRIBED = {'detail': 'Вы отписались от пользователя'}
    UNSUBSCRIBED_ERROR = {'detail': 'Вы не подписаны на этого пользователя'}

    pagination_class = RecipesUsersPagination
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        if self.action in ['list', 'retrieve']:
            return (AllowAny(),)
        return super().get_permissions()

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):

        queryset = Subscribe.objects.filter(
            subscriber=self.request.user.id
        )
        paginate_queryset = self.paginate_queryset(queryset)

        if paginate_queryset:
            serializer = SubscribeSerializer(
                paginate_queryset,
                context={'request': request},
                many=True
            )
            return self.get_paginated_response(serializer.data)

        serializer = SubscribeSerializer(
            queryset,
            context={"request": request},
            many=True
        )
        return Response(serializer.data)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated],
            serializer_class=SubscribeCreateDeleteSerializer)
    def subscribe(self, request, id):
        data_dict = {"author": id, "subscriber": request.user.id}
        serializer = SubscribeCreateDeleteSerializer(
            data=data_dict,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        if Subscribe.objects.filter(
            author=id,
            subscriber=request.user
             ).exists():
            Subscribe.objects.get(author=id, subscriber=request.user).delete()
            return Response(
                self.UNSUBSCRIBED, status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            self.UNSUBSCRIBED_ERROR, status=status.HTTP_404_NOT_FOUND
        )
