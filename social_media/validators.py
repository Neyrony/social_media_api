from django.utils import timezone


def validate_publish_at(value, exception, instance):
    if instance and (
        instance.publish_at is None or instance.publish_at < timezone.now()
    ):
        raise exception("The post is already published")

    if value is not None and value < timezone.now():
        raise exception("Publish date should be greater than the current time")

    return value
