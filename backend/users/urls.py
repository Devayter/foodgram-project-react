from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet

app_name = 'users'

router_v1 = DefaultRouter()

router_v1.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(router_v1.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken'))
]
