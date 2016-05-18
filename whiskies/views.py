import logging

from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.views.generic import ListView
from rest_framework import generics, status
from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from whiskies.command_functions import heroku_search_whiskies
from whiskies.models import Whiskey, Review, TagSearch, Tag, TagTracker
from whiskies.serializers import UserSerializer, WhiskeySerializer,\
    ReviewSerializer, TagSearchSerializer, TagSerializer, AddLikedSerializer
from whiskies.permissions import IsOwnerOrReadOnly


logger = logging.getLogger("whiskies")
tag_logger = logging.getLogger("whiskey_tag")


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


class ShootPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 120


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
    """
    To create a review send a POST request with title, text, whiskey id, and
     an optional rating from 1-100.
     Example: {"title": "Test Title", "text": "Review body text",
     "whiskey": 5, "rating": 90}
    """
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
    permission_classes = (IsOwnerOrReadOnly,)


class TagSearchListCreate(generics.ListCreateAPIView):
    queryset = TagSearch.objects.all()
    serializer_class = TagSearchSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserTagSearchList(generics.ListAPIView):

    serializer_class = TagSearchSerializer

    def get_queryset(self):
        return TagSearch.objects.filter(
            user=self.request.user)


class TagSearchDetailUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = TagSearch.objects.all()
    serializer_class = TagSearchSerializer
    permission_classes = (IsOwnerOrReadOnly,)


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
    Filter whiskies based on three optional parameters.\n
    <b>tags</b>: The titles of any Tags in the database, the endpoint
    /tag provides a list.\n
    <b>price</b>: $, $$, or $$$ for low, mid, and/or high priced whiskies.\n
    <b>region</b>: Filter by one or more regions.\n

    For example a valid query could look like
    "/shoot/?region=highland&tags=chocolate&price=1"

    The price ranges are broken down as:
    1: price <=40
    2: 40< price <= 75
    3: 75< price
    """

    serializer_class = WhiskeySerializer
    pagination_class = ShootPagination

    def get_queryset(self):

        if self.request.user.pk and self.request.user.profile.disliked_whiskies.all():

            dislikes = self.request.user.profile.disliked_whiskies.all().\
                values_list('pk', flat=True)

            qs = Whiskey.objects.exclude(pk__in=dislikes)
        else:
            qs = Whiskey.objects.all()

        if "region" in self.request.query_params:
            regions = self.request.query_params['region'].split(',')
            regions = [x.capitalize() for x in regions]
            qs = qs.filter(region__in=regions)

        if "price" in self.request.query_params:
            price_ranges = {'$': [x for x in range(1,41)],
                            '$$': [x for x in range(41, 76)],
                            '$$$': [x for x in range(76, 300)]}
            prices = []
            for price in self.request.query_params["price"].split(","):
                prices += price_ranges.get(price, [])

            qs = qs.filter(price__in=prices)

        if "tags" not in self.request.query_params:
            return qs
        else:
            tag_titles = self.request.query_params['tags'].split(',')
            a = qs.filter(tagtracker__tag__title__in=tag_titles)
            b = a.annotate(tag_count=Sum('tagtracker__normalized_count'))
            results = b.order_by('-tag_count')

            return results


class RegionList(APIView):
    """
    All unique whiskey regions with 'number' equal to their number of
    occurances in the database.
    """

    def get(self, request, format=None):
        data = Whiskey.objects.values("region").annotate(number=Count("pk"))
        return Response(data)


class TextSearchBox(APIView):
    """
    Elasticsearch of Whiskey titles.
    """

    def get(self, request, format=None):
        search = request.query_params['terms']
        terms = search.split(",")
        res = heroku_search_whiskies([x.lower() for x in terms])
        hits = res['hits']['hits']
        return Response([hit["_source"] for hit in hits])


"""
Unused views for local testing.
"""

class AllWhiskey(ListView):
    template_name = "whiskies/all_whiskies.html"
    queryset = Whiskey.objects.all()
    context_object_name = "whiskies"
