from django.urls import include, path


app_name = 'users'


urlpatterns = [
    path('api/v1/', include('djoser.urls')),
]
