from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (
   GetSubscribeView, LogInView, LogOutView, SetPasswordView, SubscribeViewSet,
   UserViewSet, UserMeAPIView
)

app_name = 'users'

router_v1 = DefaultRouter()

router_v1.register('subscribe', SubscribeViewSet, basename='subscribe')
router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/token/', include([
        path('login/', LogInView.as_view()),
        path('logout/', LogOutView.as_view())
    ])),
    path('users/', include([
        path('me/', UserMeAPIView.as_view(
            {'get': 'retrieve', 'patch': 'partial_update'})),
        path('set_password/', SetPasswordView.as_view()),
        re_path(r'(?P<user_id>\d+)/subscribe', GetSubscribeView.as_view(
            {'post': 'create', 'delete': 'destroy'}
        ))
    ])),
    path('', include(router_v1.urls))
]
