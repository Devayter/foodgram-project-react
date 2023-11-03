from django.shortcuts import redirect


def custom404(request, exception=None):
    return redirect('После деплоя здесь будет домашняя страница')
