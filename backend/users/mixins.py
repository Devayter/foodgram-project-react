from rest_framework import mixins, viewsets


class UserMeViewSetMixin(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    """Базовый класс для класса UserMeAPIView"""

    pass
