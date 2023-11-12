from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .constants import (
                        NOT_SUBSCRIBED,
                     SELF_SUBSCRIPTION_ERROR,
                        SUBSCRIPTION_ALREADY_EXISTS, UNSUBSCRIBED,
                        )
from .models import Subscribe, User
from recipes.pagination import RecipesUsersPagination
from .serializers import SubscribeSerializer, UserSerializer


class UserViewSet(DjoserViewSet):
    """Вьюсет для регистрации"""

    pagination_class = RecipesUsersPagination
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

    # @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    # def subscribtions(self, request):
    #     queryset = Subscribe.objects.filter(
    #         subscriber=self.request.user.id
    #     ).values('author')
    #     # print('>>>>', paginate_qweryset)
    #     # serializer = SubscribeSerializer(data=paginate_qweryset)
    #     # serializer.is_valid(raise_exception=True)
    #     # return Response(serializer.data, status=status.HTTP_200_OK)
    #     page = self.paginate_queryset(queryset)
    #     serializer = self.get_pagination_serializer(page)
    #     return Response(serializer.data)

    #     # paginated_subscriptions = self.paginator.paginate_queryset(queryset, self.request)
    #     # serializer = SubscribeSerializer(paginated_subscriptions, many=True)
    #     # data = paginated.data
    #     paginated = self.get_paginated_response(data)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    #     return self.paginator.get_paginated_response(serializer.data)


    # def get_queryset(self):
    #     print('>>>>>>', Subscribe.objects.filter(
    #         subscriber=self.request.user
    #     ).values('author'))
    #     return Subscribe.objects.filter(
    #         subscriber=self.request.user.id
    #     ).values('author')
