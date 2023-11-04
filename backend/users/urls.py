from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    SetPasswordView, LogInView, LogOutView, UserViewSet, UserMeAPIView
)

app_name = 'users'

router_v1 = DefaultRouter()

router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/token/', include([
        path('login/', LogInView.as_view()),
        path('logout/', LogOutView.as_view())
    ])),
    path('users/me/', UserMeAPIView.as_view(
        {'get': 'retrieve', 'patch': 'partial_update'})),
    path('users/set_password/', SetPasswordView.as_view()),
    path('', include(router_v1.urls))
]
