from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from .models import BlacklistedToken


@shared_task
def delete_expired_blacklisted_tokens():
    """Планировщик задач для чистки черного списка токенов доступа"""
    ten_days_ago = timezone.now() - timedelta(days=10)
    BlacklistedToken.objects.filter(blacklisted_at__lt=ten_days_ago).delete()
