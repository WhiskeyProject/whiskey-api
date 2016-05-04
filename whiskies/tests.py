from django.core.urlresolvers import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from rest_framework.authtoken.models import Token
from whiskies.models import Whiskey, Review, Profile


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
        self.assertEqual(response.data[0]['username'], self.user.username)

        profile = response.data[0].get('profile', None)
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
        self.assertEqual(len(response.data), Whiskey.objects.count())

    def test_retrieve_whiskey(self):
        url = reverse("list_whiskey")
        whiskey = self.whiskies[0]
        response = self.client.get(url, {"pk": whiskey.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(whiskey.price, response.data[0].get('price', None))


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
        self.assertEqual(len(response.data), Review.objects.count())

    def test_retrieve_review(self):
        url = reverse("list_review")
        response = self.client.get(url, {"pk": self.review.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.review.text, response.data[0].get('text', None))

    def test_create_review(self):
        url = reverse("list_review")

        token = Token.objects.get(user_id=self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        data = {"whiskey": self.whiskey.id,
                "text": "testing"}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 2)


# Check for adding duplicates and removing ones that are not present.
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


# Comparables
# TagSearch default name

