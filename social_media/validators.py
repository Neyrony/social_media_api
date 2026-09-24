from django.utils import timezone


def validate_publish_at(value, exception, instance):
    if instance:
        original_obj = type(instance).objects.get(pk=instance.pk)
        if original_obj.publish_at is None or original_obj.publish_at < timezone.now():
            raise exception("The post is already published")
    if value is not None and value < timezone.now():
        raise exception("Publish date should be greater than the current time")

    return value
