from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


class PublicUserApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user_succes(self):
        payload = {
            "email": "test1@example.com",
            "name": "testname",
            "password": "password123",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))

        self.assertEqual(user.name, payload["name"])

        self.assertNotIn("password", res.data)

    def test_create_user_fail_email_already_exit(self):
        payload = {
            "email": "test2@example.com",
            "name": "testname",
            "password": "password123",
        }
        user = get_user_model().objects.create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_fail_short_password(self):
        payload = {
            "email": "test3@example.com",
            "name": "testname",
            "password": "pw",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exit = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertFalse(user_exit)

    def test_create_token_succes_for_user(self):
        user_detail = {
            "email": "test4@example.com",
            "name": "testname",
            "password": "password",
        }
        user = get_user_model().objects.create_user(**user_detail)
        payload = {
            "email": "test4@example.com",
            "password": "password",
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_fail_incorect_creditionals(self):
        user_detail = {
            "email": "test4@example.com",
            "name": "testname",
            "password": "password1234",
        }
        user = get_user_model().objects.create_user(**user_detail)
        payload = {
            "email": "test4@example.com",
            "password": "password123",
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_fail_blank_password(self):
        user_detail = {
            "email": "test4@example.com",
            "name": "testname",
            "password": "password1234",
        }
        user = get_user_model().objects.create_user(**user_detail)
        payload = {
            "email": "test4@example.com",
            "password": "",
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unathorized(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApi(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            name="testname", email="test@example.com", password="password1234"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_profile_succes(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data,
            {
                "name": self.user.name,
                "email": self.user.email,
            },
        )

    def test_post_me_not_allowed(self):
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        payload = {"name": "updated_name", "password": "new_password"}
        res = self.client.patch(
            ME_URL,
            payload,
        )
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
