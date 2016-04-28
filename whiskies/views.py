from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.generic import ListView
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response

from whiskies.models import Whiskey, Review, TagSearch, Tag
from whiskies.serializers import UserSerializer, WhiskeySerializer,\
    ReviewSerializer, TagSearchSerializer, TagSerializer, TagTrackerSerializer, \
    AddLikedSerializer

"""
Only create/delete Whiskey in the admin.

notes: double check permissions, might need need to switch some to
OwnerOrReadOnly.
"""


class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


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
    Put request needs only a whiskey_id.
    Example: {"whiskey_id": 5}
    """

    def put(self, request, format=None):

        user = request.user
        serializer = AddLikedSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save(whiskey_id = request.data["whiskey_id"])
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






