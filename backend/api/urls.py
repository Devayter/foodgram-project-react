from django.urls import include, path


app_name = 'api'

urlpatterns = [
    path('v1/', include('recipes.urls')),
    # path('v1/', include('users.urls'))
]
