from unittest import TestCase

import numpy as np
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from django.core.management import call_command

from whiskies.command_functions import get_tag_counts, create_features_dict, \
    update_whiskey_comps, clear_saved, create_scores, main_scores
from whiskies.models import Whiskey, Review, Tag, TagTracker
from whiskies.views import add_tag_to_whiskey


class UserTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="Tester",
                                             password="pass_word")

        self.url = reverse("list_users")

    def test_create_user(self):
        data = {"username": "Tester2", "password": "pass_word",
                "email": "test@gmail"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

        self.assertEqual(Token.objects.count(), User.objects.count())

    def test_retrieve_user(self):
        response = self.client.get(self.url,{"pk": self.user.id},
                                   format="json")
        self.assertEqual(response.data['results'][0]['username'],
                         self.user.username)

        profile = response.data['results'][0].get('profile', None)
        self.assertNotEqual(profile, None)


class WhiskeyTest(APITestCase):

    def setUp(self):
        self.whiskies = [
            Whiskey.objects.create(title="test", price=x, rating=x)
            for x in range(1, 4)
            ]

    def test_retrieve_whiskey_list(self):
        url = reverse("list_whiskey")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']),
                         Whiskey.objects.count())

    def test_retrieve_whiskey(self):
        url = reverse("list_whiskey")
        whiskey = self.whiskies[0]
        response = self.client.get(url, {"pk": whiskey.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(whiskey.price,
                         response.data['results'][0].get('price', None))


class ReviewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="Tester",
                                             password="pass_word")
        self.whiskey = Whiskey.objects.create(title="test", price=5, rating=5)

        self.review = Review.objects.create(user=self.user,
                                            whiskey=self.whiskey,
                                            text="this is a test review")

    def test_list_reviews(self):
        url = reverse("list_review")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), Review.objects.count())

    def test_retrieve_review(self):
        url = reverse("list_review")
        response = self.client.get(url, {"pk": self.review.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.review.text,
                         response.data['results'][0].get('text', None))

    def test_create_review(self):
        url = reverse("list_review")

        token = Token.objects.get(user_id=self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        data = {"whiskey": self.whiskey.id,
                "text": "testing",
                "title": "test"}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 2)


class ChangeLikesTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="Tester",
                                             password="pass_word")
        self.whiskey = Whiskey.objects.create(title="test", price=5, rating=5)

    def test_add_remove_like(self):

        token = Token.objects.get(user_id=self.user.id)
        url = reverse("change_liked_whiskey")

        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        data = {"whiskey_id": self.whiskey.id,
                "opinion": "like",
                "action": "add"}

        response = self.client.put(url, data, format='json')

        num_saved = self.user.profile.liked_whiskies.count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(num_saved, 1)

        remove_data = {"whiskey_id": self.whiskey.id,
                       "opinion": "like",
                       "action": "remove"}

        remove_response = self.client.put(url, remove_data, format='json')
        new_num_saved = self.user.profile.liked_whiskies.count()
        self.assertEqual(remove_response.status_code, status.HTTP_200_OK)
        self.assertEqual(new_num_saved, 0)

    def test_add_remove_dislike(self):

        token = Token.objects.get(user_id=self.user.id)
        url = reverse("change_liked_whiskey")

        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        data = {"whiskey_id": self.whiskey.id,
                "opinion": "dislike",
                "action": "add"}

        response = self.client.put(url, data, format='json')

        num_saved = self.user.profile.disliked_whiskies.count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(num_saved, 1)

        remove_data = {"whiskey_id": self.whiskey.id,
                       "opinion": "dislike",
                       "action": "remove"}

        remove_response = self.client.put(url, remove_data, format='json')
        new_num_saved = self.user.profile.disliked_whiskies.count()
        self.assertEqual(remove_response.status_code, status.HTTP_200_OK)
        self.assertEqual(new_num_saved, 0)


class TagTrackerSearchTest(APITestCase):
    """
    Test for tagtracker creation.
    Test shoot endpoint with tag, price, and region filters.
    """

    def setUp(self):
        self.whiskey1 = Whiskey.objects.create(title="whiskey1",
                                               price=10,
                                               rating=10,
                                               region="A")
        self.whiskey2 = Whiskey.objects.create(title="whiskey2",
                                               price=50,
                                               rating=20,
                                               region="A")
        self.whiskey3 = Whiskey.objects.create(title="whiskey3",
                                               price=90,
                                               rating=30,
                                               region="B")

        self.tags = [Tag.objects.create(title="tag{}".format(x))
                     for x in range(1, 4)]

        self.url = reverse("search_list")

    def test_tagtracker_add_count(self):
        tracker = TagTracker.objects.create(whiskey=self.whiskey1,
                                            tag=self.tags[0],
                                            count=2)
        tracker.add_count()
        self.assertEqual(tracker.count, 3)

        tracker.add_count(5)
        self.assertEqual(tracker.count, 8)

    def test_tag_search(self):
        tracker1 = TagTracker.objects.create(whiskey=self.whiskey1,
                                             tag=self.tags[0],
                                             count=5,
                                             normalized_count=5)
        tracker2 = TagTracker.objects.create(whiskey=self.whiskey3,
                                             tag=self.tags[0],
                                             count=3,
                                             normalized_count=3)

        response = self.client.get(self.url + "?tags=tag1")
        results = response.data['results']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results[0]['title'], self.whiskey1.title)
        self.assertEqual(results[1]['title'], self.whiskey3.title)
        self.assertEqual(len(results), 2)

    def test_price_search(self):
        response = self.client.get(self.url + "?price=$")
        results = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 1)

        response = self.client.get(self.url + "?price=$,$$$")
        results = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 2)

    def test_region_search(self):
        response = self.client.get(self.url + "?region=a")
        results = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 2)

        response = self.client.get(self.url + "?price=$$$&region=a")
        results = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(results)


class ComparablesTest(APITestCase):
    """
    For testing the creation of comparables.
    Note that numpy arrays must be called with .all() in order for
    assertEqual to work.
    """

    def setUp(self):
        self.whiskey1 = Whiskey.objects.create(title="whiskey1",
                                               price=10,
                                               rating=10,
                                               region="A")

        self.whiskey2 = Whiskey.objects.create(title="whiskey2",
                                               price=50,
                                               rating=20,
                                               region="A")
        self.whiskey3 = Whiskey.objects.create(title="whiskey3",
                                               price=90,
                                               rating=30,
                                               region="B")

        self.tags = [Tag.objects.create(title=x) for x in 'abc']

        TagTracker.objects.create(whiskey=self.whiskey1,
                                  tag=self.tags[0],
                                  count=2,
                                  normalized_count=2)
        TagTracker.objects.create(whiskey=self.whiskey1,
                                  tag=self.tags[1],
                                  count=3,
                                  normalized_count=3)

        TagTracker.objects.create(whiskey=self.whiskey2,
                                  tag=self.tags[0],
                                  count=2,
                                  normalized_count=2)
        TagTracker.objects.create(whiskey=self.whiskey3,
                                  tag=self.tags[0],
                                  count=3,
                                  normalized_count=3)

    def test_get_tag_counts(self):
        whiskey1_array = get_tag_counts(self.whiskey1, self.tags)
        whiskey2_array = get_tag_counts(self.whiskey2, self.tags)

        self.assertEqual(whiskey1_array.all(), np.array([2, 3, 0]).all())
        self.assertEqual(whiskey2_array.all(), np.array([2, 0, 0]).all())

    def create_features_dict_test(self):
        features = create_features_dict(Whiskey.objects.all(), self.tags)

        self.assertEqual(features[1].all(), np.array([2, 3, 0]).all())
        self.assertEqual(features[3].all(), np.array([3, 0, 0]).all())

    def test_create_scores(self):
        features = create_features_dict(Whiskey.objects.all(), self.tags)
        whiskey_ids = Whiskey.objects.values_list("pk", flat=True)
        scores = create_scores(whiskey_ids, features)

        first_whiskey = scores[0]
        second_whiskey = scores[1]

        self.assertLess(first_whiskey[self.whiskey2.id],
                        first_whiskey[self.whiskey3.id])
        self.assertLess(second_whiskey[self.whiskey3.id],
                        second_whiskey[self.whiskey1.id])

    def test_main_scores(self):
        scores_df = main_scores(Whiskey.objects.all(), self.tags)
        first_whiskey = scores_df.loc[self.whiskey1.id].values
        third_whiskey = scores_df[self.whiskey3.id].values

        self.assertLess(first_whiskey[1],
                        first_whiskey[2])

        self.assertLess(third_whiskey[1],
                        third_whiskey[0])

    def update_whiskey_comps_test(self):

        update_whiskey_comps(Whiskey.objects.all(),
                             self.tags,
                             number_comps=1)

        self.assertEqual(self.whiskey1.comparable.first(), self.whiskey2)
        self.assertEqual(self.whiskey2.comparable.first(), self.whiskey3)

        clear_saved(self.whiskey1)

        self.assertFalse(self.whiskey1.comparable.first())

    def test_set_comp(self):
        clear_saved(self.whiskey1)

        kwargs = {"number": 1}
        call_command("set_comps", **kwargs)
        self.assertEqual(self.whiskey1.comparables.count(), 1)

        clear_saved(self.whiskey1)

        kwargs = {"number": 2}
        call_command("set_comps", **kwargs)
        self.assertEqual(self.whiskey1.comparables.count(), 2)


class AddTagToWhiskeyTest(APITestCase):

    def setUp(self):
        self.whiskey1 = Whiskey.objects.create(title="whiskey1",
                                               price=10,
                                               rating=10)
        self.tag1 = Tag.objects.create(title="tag1")

    def test_add_tag_to_whiskey(self):

        self.assertFalse(TagTracker.objects.first())

        add_tag_to_whiskey(self.whiskey1, self.tag1)
        self.assertEqual(TagTracker.objects.first().count, 1)

        add_tag_to_whiskey(self.whiskey1, self.tag1)
        self.assertEqual(TagTracker.objects.first().count, 2)


class TextSearchBoxTest(APITestCase):

    def setUp(self):
        self.whiskey1 = Whiskey.objects.create(title="first whiskey",
                                               price=10,
                                               rating=10)
        self.whiskey1 = Whiskey.objects.create(title="second whiskey",
                                               price=10,
                                               rating=10)
        self.whiskey1 = Whiskey.objects.create(title="third whiskey",
                                               price=10,
                                               rating=10)

    def test_get_results(self):
        url = reverse("search_box")
        response = self.client.get(url + "?terms=first")
        results = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], "Mackmyra First Edition")
