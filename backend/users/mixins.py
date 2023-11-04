from rest_framework import mixins, viewsets


class CreateDestroyListMixin(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Базовый класс для SubscribeViewSet"""

    pass


class UserMeViewSetMixin(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    """Базовый класс для класса UserMeAPIView"""

    pass
