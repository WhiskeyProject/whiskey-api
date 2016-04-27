from django.contrib import admin

from whiskies.models import Whiskey, Tag, TagSearch, TagTracker, Review


@admin.register(Whiskey)
class WhiskeyAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "img_url", "price", "rating")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "title")


@admin.register(TagTracker)
class TagTrackerAdmin(admin.ModelAdmin):
    list_display = ("id", "count", "whiskey", "tag")


