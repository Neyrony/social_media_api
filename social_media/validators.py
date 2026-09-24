from django.utils import timezone


def validate_publish_at(value, exception, instance):
    if value is not None and value < timezone.now():
        raise exception("Publish date should be greater than the current time")

    if instance and instance.publish_at and instance.publish_at < timezone.now():
        raise exception("The post is already published")

    return value
