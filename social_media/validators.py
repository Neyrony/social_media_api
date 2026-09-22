import datetime

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_publish_at(date: datetime.datetime | None) -> None:
    if date is not None and date <= timezone.now():
        raise ValidationError("Publish date should be greater than the current time")
