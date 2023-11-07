from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from .constants import INVALID_TOKEN
from .models import BlacklistedToken


class BlacklistTokenMiddleware:
    """Middleware для проверки токена на черный список"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token:
            token = token[7:]
            if BlacklistedToken.objects.filter(token=token).exists():
                response = Response(
                    {'detail': INVALID_TOKEN},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                response.accepted_renderer = JSONRenderer()
                response.accepted_media_type = "application/json"
                response.renderer_context = {}
                response.render()
                return response

        return self.get_response(request)
