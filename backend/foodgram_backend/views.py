from django.shortcuts import redirect


def custom404(request, exception=None):
    '''Переадресация на главную страницу сайта при ошибке 404'''
    return redirect('После деплоя здесь будет домашняя страница')
