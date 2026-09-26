from django.utils import timezone


def validate_publish_at(value, exception, instance):
    if instance and instance.pk:
        if instance.is_published and value != instance.publish_at:
            raise exception("Post is already published you cant change this value")
        elif not instance.is_published:
            if value is None:
                raise exception("You cant set date to empty")
            elif value is not None and value < timezone.now():
                raise exception("This value should be greater than time now")

            return value

    if value is not None and value <= timezone.now():
        raise exception("This value should be greater than time now")

    return value
