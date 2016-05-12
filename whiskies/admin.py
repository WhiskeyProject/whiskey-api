from django.contrib import admin
from django.db import models

from whiskies.models import Whiskey, Tag, TagSearch, TagTracker, Review,\
    Profile


@admin.register(Whiskey)
class WhiskeyAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "rating", "img_url")

    search_fields = ["title", "description"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category")


@admin.register(TagTracker)
class TagTrackerAdmin(admin.ModelAdmin):
    list_display = ("id", "tag", "whiskey", "count")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "rating", "text", "whiskey", "user")

@admin.register(TagSearch)
class TagSearchAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "search_string", "created_at")
