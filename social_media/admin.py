from django.contrib import admin
from django.contrib.auth.models import Group

from social_media.models import Profile, Post, Comment, Hashtag

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Hashtag)

admin.site.unregister(Group)
