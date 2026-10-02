from django.apps import AppConfig


class SocialMediaConfig(AppConfig):
    name = "social_media"

    def ready(self):
        import social_media.signals
