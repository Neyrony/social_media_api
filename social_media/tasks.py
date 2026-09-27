from celery import shared_task
from django.utils import timezone

from social_media.models import Post


@shared_task
def publish_post():
    post_to_publish = Post.objects.filter(
        is_published=False, publish_at__lte=timezone.now()
    )
    post_to_publish.update(is_published=True)
