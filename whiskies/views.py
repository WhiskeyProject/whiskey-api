from functools import reduce

from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.generic import ListView
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
import operator
from django.db.models import Q

from whiskies.models import Whiskey, Review, TagSearch, Tag, Profile, \
    TagTracker
from whiskies.serializers import UserSerializer, WhiskeySerializer,\
    ReviewSerializer, TagSearchSerializer, TagSerializer, TagTrackerSerializer, \
    AddLikedSerializer, ProfileSerializer

import cloudinary
import cloudinary.uploader
import cloudinary.api

"""
Only create/delete Whiskey in the admin.

notes: double check permissions, might need need to switch some to
OwnerOrReadOnly.
"""


class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        permissions.AllowAny
    ]


class UserDetail(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class WhiskeyList(generics.ListAPIView):
    queryset = Whiskey.objects.all()
    serializer_class = WhiskeySerializer


class WhiskeyDetail(generics.RetrieveAPIView):
    queryset = Whiskey.objects.all()
    serializer_class = WhiskeySerializer


class ReviewListCreate(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        whiskey_id = self.request.data["whiskey"]

        serializer.save(user=self.request.user,
                        whiskey=Whiskey.objects.get(pk=whiskey_id))


class ReviewDetailUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class TagSearchListCreate(generics.ListCreateAPIView):
    queryset = TagSearch.objects.all()
    serializer_class = TagSearchSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserTagSearchList(generics.ListAPIView):

    serializer_class = TagSearchSerializer

    def get_queryset(self):
        return TagSearch.objects.filter(
            user=self.request.user).order_by("created_at")


class TagSearchDetailUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = TagSearch.objects.all()
    serializer_class = TagSearchSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class TagListCreate(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class TagDetailUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class WhiskeyLikeUpdate(APIView):
    """
    Put request needs a whiskey_id, action ['add', 'remove'], and
    opinion ['like', 'dislike'].
    Example: {"whiskey_id": 5, "action": "remove", "opinion": "like"}
    """

    def put(self, request, format=None):

        user = request.user
        serializer = AddLikedSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save(whiskey_id=request.data["whiskey_id"],
                            action=request.data["action"],
                            opinion=request.data["opinion"])

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikedWhiskeyList(generics.ListAPIView):
    """
    A GET request returns all of the requesting user's liked whiskies.
    """
    queryset = Whiskey.objects.all()
    serializer_class = WhiskeySerializer

    def get_queryset(self):

        return self.request.user.profile.liked_whiskies.all()


class DislikedWhiskeyList(generics.ListAPIView):
    """
    A GET request returns all of the requesting user's disliked whiskies.
    """
    queryset = Whiskey.objects.all()
    serializer_class = WhiskeySerializer

    def get_queryset(self):

        return self.request.user.profile.disliked_whiskies.all()


class SearchList(generics.ListCreateAPIView):
    """
    Filter Whiskies based on tag title querystring.
    Example: /shoot/?tags=tag1,tag2
    """

    serializer_class = WhiskeySerializer

    def get_queryset(self):
        # Use custom manager?

        if "tags" not in self.request.query_params:
            return []

        if self.request.user.pk:

            dislikes = self.request.user.profile.disliked_whiskies.all().\
                values_list('pk', flat=True)

            qs = Whiskey.objects.exclude(pk__in=dislikes)

            #  Do not create a TagSearch if user is anonymous or the search
            #  would be a duplicate for that user.
            if not TagSearch.objects.filter(
                    user=self.request.user,
                    search_string=self.request.query_params['tags']).first():

                TagSearch.objects.create(
                    user=self.request.user,
                    search_string=self.request.query_params['tags']
                )
        else:
            qs = Whiskey.objects.all()

        tag_titles = self.request.query_params['tags'].split(',')
        #Whiskey.objects.filter(tagtracker__tag__in=[]).annotate(Sum(tagtra).filter(sum_count__gt=0)
        sorted_qs = sorted(qs, key=lambda x: x.tag_match(tag_titles),
                           reverse=True)

        results = [x for x in sorted_qs if x.tag_match(tag_titles)]
        print(len(results))
        return results


def add_tag_to_whiskey(whiskey, tag):
    """
    This will increment the tag tracker for the given whiskey and tag.
    A new tracker will be created if this is the first time the tag is
    applied to the whiskey.
    """
    tracker = TagTracker.objects.filter(whiskey=whiskey, tag=tag).first()
    if not tracker:
        tracker = TagTracker.objects.create(whiskey=whiskey, tag=tag)
    tracker.add_count()
    tracker.save()


class TextSearchBox(generics.ListAPIView):
    """
    Returns a queryset of all whiskies with a title that contains 1 or more
    of the search terms.

    example: /searchbox/?terms=term1,term2
    """

    serializer_class = WhiskeySerializer

    def get_queryset(self):

        # if "terms" not in self.request.query_params:
        #     return []

        terms = self.request.query_params['terms'].split(',')

        query = reduce(operator.or_, (
            Q(title__icontains=item) for item in terms)
                       )

        qs = Whiskey.objects.filter(query)
        return qs


"""
Template views, just for local testing
"""

class AllWhiskey(ListView):
    template_name = "whiskies/all_whiskies.html"
    queryset = Whiskey.objects.all()
    context_object_name = "whiskies"
