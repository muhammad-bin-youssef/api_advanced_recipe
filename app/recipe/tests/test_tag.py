from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status as st
from rest_framework.test import APIClient

from core import models
from recipe import serializers

from decimal import Decimal


def create_tag(user, name="test tag"):
    return models.Tag.objects.create(user=user, name=name)


def create_user(
    name="testuser",
    email="testemail@example.com",
    password="password1234",
):
    return get_user_model().objects.create_user(
        name=name, email=email, password=password
    )


def get_tag_url(id: int):
    return reverse("recipe:tag-detail", args=[id])


URL_Tag = reverse("recipe:tag-list")

URL_RECIPE = reverse("recipe:recipe-list")


class TestPublicApi(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_tag_fail(self):
        res = self.client.get(URL_Tag)
        self.assertEqual(res.status_code, st.HTTP_401_UNAUTHORIZED)


class TestPrivateApi(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@example.com", name="testname", password="password1234"
        )
        self.client.force_authenticate(user=self.user)

    def test_get_tag_succ(self):
        create_tag(user=self.user)
        create_tag(user=self.user)
        res = self.client.get(URL_Tag)
        tags = models.Tag.objects.all().order_by("-name")
        serializer = serializers.TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, st.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        user2 = create_user(email="testuser2@exmaple.com")
        tag = create_tag(user=self.user, name="Fruity")
        create_tag(user=user2, name="Dinner")
        res = self.client.get(URL_Tag)
        self.assertEqual(res.status_code, st.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_update_tag(self):
        tag = create_tag(user=self.user)
        res = self.client.patch(get_tag_url(tag.id), {"name": "updated tag"})
        self.assertEqual(res.status_code, st.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, "updated tag")

    def test_delete_tag(self):
        tag = create_tag(user=self.user)
        res = self.client.delete(get_tag_url(tag.id))
        exist = models.Tag.objects.filter(user=self.user).exists()
        self.assertEqual(res.status_code, st.HTTP_204_NO_CONTENT)
        self.assertFalse(exist)

    def test_create_recipe_with_new_tags(self):
        payload = {
            "title": "Sample recipe",
            "time_minutes": 30,
            "price": Decimal("5.99"),
            "tags": [
                {"name": "Desert"},
                {"name": "Dinner"},
            ],
        }
        res = self.client.post(URL_RECIPE, payload, format="json")
        recipes = models.Tag.objects.filter(user=self.user)
        self.assertEqual(res.status_code, st.HTTP_201_CREATED)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload["tags"]:
            exists = models.Tag.objects.filter(user=self.user, name=tag["name"])
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        tag_des = create_tag(user=self.user, name="Desert")
        payload = {
            "title": "Sample recipe",
            "time_minutes": 30,
            "price": Decimal("5.99"),
            "tags": [
                {"name": "Desert"},
                {"name": "Breakfast"},
            ],
        }
        res = self.client.post(URL_RECIPE, payload, format="json")
        recipes = models.Tag.objects.filter(user=self.user)
        self.assertEqual(res.status_code, st.HTTP_201_CREATED)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.count(), 2)
        self.assertIn(tag_des, recipe.tags.all())
        for tag in payload["tags"]:
            exists = models.Tag.objects.filter(user=self.user, name=tag["name"])
            self.assertTrue(exists)

        # BUG:
