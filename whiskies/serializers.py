from django.contrib.auth.models import User
from rest_framework import serializers

from whiskies.models import Whiskey, Profile, Review, TagSearch, Tag,\
    TagTracker


class WhiskeySerializer(serializers.ModelSerializer):
    reviews = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    # might need to go through TagTracker
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Whiskey
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):

    # check that liked and disliked whiskies are displayed



    class Meta:
        model = Profile
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):

    reviews = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    tag_searches = serializers.PrimaryKeyRelatedField(many=True,
                                                      read_only=True)

    class Meta:
        model = User
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    # Set user and whiskey in the view. Not sure on whiskey though.

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    whiskey = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    # I don't think tag cares about tag_searches

    # set whiskey in the view when a tag is created.

    whiskies = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Tag
        fields = "__all__"


class TagSearchSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = TagSearch
        fields = "__all__"


class TagTrackerSerializer(serializers.ModelSerializer):

    # Not sure if this is needed for anything.

    class Meta:
        model = TagTracker
        fields = "__all__"
