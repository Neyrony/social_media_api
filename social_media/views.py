from rest_framework.viewsets import ModelViewSet

from social_media.models import Post
from social_media.serializers import (
    PostListSerializer,
    PostRetrieveSerializer,
    PostSerializer,
)


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        elif self.action == "retrieve":
            return PostRetrieveSerializer
        return PostSerializer
