from django.contrib import admin

from whiskies.models import Whiskey, Tag, TagSearch, TagTracker, Review,\
    Profile, WhiskeyFact


@admin.register(Whiskey)
class WhiskeyAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "rating", "region", "review_count",
                    "img_url", "list_img_url", "detail_img_url")

    search_fields = ["title", "description", "region"]

    list_display_links = ("id", "title", "img_url", "price", "rating",
                          "region", "review_count")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category")


@admin.register(TagTracker)
class TagTrackerAdmin(admin.ModelAdmin):
    list_display = ("id", "tag", "whiskey", "count", "normalized_count")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "rating", "text", "whiskey", "user")


@admin.register(TagSearch)
class TagSearchAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "search_string", "created_at")


@admin.register(WhiskeyFact)
class WhiskeyFactAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "created_at")
