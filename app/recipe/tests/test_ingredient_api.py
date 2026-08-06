from decimal import Decimal
from core import models
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status as st
from rest_framework.test import APIClient
from recipe import serializers

URL_INGREDIENT = reverse("recipe:ingredient-list")


def create_user(email="test@gmail.com", password="password1234"):
    return get_user_model().objects.create_user(email=email, password=password)


def create_ingredient(user, name="ingredient"):
    return models.Ingredient.objects.create(user=user, name=name)


def get_detial_url(id: int):
    return reverse("recipe:ingredient-detail", args=[id])


class PublicApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_unathonticated_user(self):
        res = self.client.get(URL_INGREDIENT)
        self.assertEqual(res.status_code, st.HTTP_401_UNAUTHORIZED)


class PrivateApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_get_list_athonticated_user(self):
        create_ingredient(user=self.user, name="Flower")
        create_ingredient(user=self.user, name="Sougar")
        res = self.client.get(URL_INGREDIENT)
        ingredients = models.Ingredient.objects.all().order_by("-name")
        serializer = serializers.IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, st.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_limited_to_user(self):
        another_user = create_user(email="test2@gmail.com")
        ingredient = create_ingredient(user=self.user, name="Flower")
        create_ingredient(user=another_user, name="Sougar")
        res = self.client.get(URL_INGREDIENT)
        self.assertEqual(res.status_code, st.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)
        self.assertEqual(res.data[0]["id"], ingredient.id)

    def test_update_ingredient(self):
        ingredient = create_ingredient(user=self.user)
        payload = {"name": "updated"}
        res = self.client.patch(get_detial_url(ingredient.id), payload)
        ingredient.refresh_from_db()
        self.assertEqual(res.status_code, st.HTTP_200_OK)
        self.assertEqual(payload["name"], ingredient.name)

    def test_delete_ingredient(self):
        ingredient = create_ingredient(user=self.user)
        res = self.client.delete(get_detial_url(ingredient.id))
        exist = models.Ingredient.objects.filter(user=self.user).exists()
        self.assertEqual(res.status_code, st.HTTP_204_NO_CONTENT)
        self.assertFalse(exist)
