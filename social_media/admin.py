from django.contrib import admin
from django.contrib.auth.models import Group

from social_media.models import Profile, Post, Comment, Hashtag


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("username", "bio", "user")
    search_fields = ("username", "user__email")
    ordering = ("username",)
    filter_horizontal = ("following",)
    list_per_page = 25


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "content", "owner", "created_at")
    search_fields = ("title", "content", "owner__username")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    filter_horizontal = ("hashtags", "liked_by")
    readonly_fields = ("is_published",)
    list_per_page = 25


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("content", "owner", "post", "created_at")
    search_fields = ("content", "owner__username")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    list_per_page = 25


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
    list_per_page = 25


admin.site.unregister(Group)
