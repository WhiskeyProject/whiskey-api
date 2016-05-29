"""WhiskeyProof URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.authtoken.views import obtain_auth_token
from django.views.decorators.cache import cache_page

from whiskies.views import UserListCreate, UserDetail, WhiskeyList,\
    WhiskeyDetail, ReviewListCreate, ReviewDetailUpdateDelete,\
    TagSearchListCreate, TagSearchDetailUpdateDelete, TagListCreate,\
    TagDetailUpdateDelete, WhiskeyLikeUpdate, LikedWhiskeyList,\
    DislikedWhiskeyList, AllWhiskey, SearchList, UserTagSearchList,\
    TextSearchBox, RegionList, WhiskeyFactList, LocalSearchBox, \
    PlaceholderSearch

urlpatterns = [
    url(r'^users/$', UserListCreate.as_view(), name="list_users"),
    url(r'^users/(?P<pk>\d+)/$', UserDetail.as_view(), name="detail_user"),

    url(r'^whiskey/$', WhiskeyList.as_view(), name="list_whiskey"),
    url(r'^whiskey/(?P<pk>\d+)/$', WhiskeyDetail.as_view(),
        name="detail_whiskey"),

    url(r'^likedwhiskey/$', LikedWhiskeyList.as_view(),
        name="liked_whiskey"),
    url(r'^dislikedwhiskey/$', DislikedWhiskeyList.as_view(),
        name="Disliked_whiskey"),

    url(r'^changeliked/$', WhiskeyLikeUpdate.as_view(),
        name="change_liked_whiskey"),

    url(r'^review/$', ReviewListCreate.as_view(), name="list_review"),
    url(r'^review/(?P<pk>\d+)/$', ReviewDetailUpdateDelete.as_view(),
        name="detail_review"),

    url(r'^tag/$', TagListCreate.as_view(), name="list_tag"),
    url(r'^tag/(?P<pk>\d+)/$', TagDetailUpdateDelete.as_view(),
        name="detail_tag"),

    url(r'^region/$', RegionList.as_view(), name="region_list"),

    url(r'^tagsearch/$', TagSearchListCreate.as_view(), name="list_tagsearch"),
    url(r'^usersearches/$', UserTagSearchList.as_view(),
        name="user_list_tagsearch"),
    url(r'^tagsearch/(?P<pk>\d+)/$', TagSearchDetailUpdateDelete.as_view(),
        name="detail_tagsearch"),

    url(r'^searchbox/$', TextSearchBox.as_view(), name="search_box"),
    #url(r'^searchbox/$', PlaceholderSearch.as_view(), name="search_box"),

    url(r'^testsearchbox/$', LocalSearchBox.as_view(), name="test_search_box"),
    #url(r'^testsearch/$', TestSearch.as_view(), name="test_search"),

    url(r'^shoot/$', cache_page(60 * 60 * 8)(SearchList.as_view()),
        name="search_list"),

    url(r'^randomfact/$', WhiskeyFactList.as_view(), name="random_fact"),

    url(r'^allwhiskey/$', AllWhiskey.as_view(), name="test_list"),

    url(r'api-token-auth/$', obtain_auth_token),

    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^admin/', admin.site.urls),
    url('^', include('django.contrib.auth.urls')),
]
#cache_page(60 * 2)