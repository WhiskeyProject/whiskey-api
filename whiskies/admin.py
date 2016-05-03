from django.contrib import admin

from whiskies.models import Whiskey, Tag, TagSearch, TagTracker, Review,\
    Profile


@admin.register(Whiskey)
class WhiskeyAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "img_url", "price", "rating")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "title")


@admin.register(TagTracker)
class TagTrackerAdmin(admin.ModelAdmin):
    list_display = ("id", "count", "whiskey", "tag")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("rating", "text", "whiskey", "user")

@admin.register(TagSearch)
class TagSearchAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "search_string", "created_at")
