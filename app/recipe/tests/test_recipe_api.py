from decimal import Decimal
from core import models
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status as st
from rest_framework.test import APIClient
from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse("recipe:recipe-list")


def create_recipe(user, **kw):
    payload = {
        "title": "test recipe",
        "time_minutes": 5,
        "description": "test desc",
        "price": Decimal("5.5"),
        "link": "test link",
    }
    payload.update(kw)
    recipe = models.Recipe.objects.create(user, **kw)
    return recipe


class PublicRecipeTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_requiered_fail(self):
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, st.HTTP_401_UNAUTHORIZED)


class PrivateRecipeTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testrecipe@exaple.com",
            password="password1234",
        )
        self.client.force_authenticate(self.user)

    def test_retrive_recipe(self):
        create_recipe(self.user)
        create_recipe(self.user)

        res = self.client.get(RECIPE_URL)

        recipe = models.Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, st.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_limited_to_user(self):
        other_user = get_user_model().objects.create_user(
            email="2testrecipe@exaple.com",
            password="password1234",
        )
        create_recipe(other_user)
        create_recipe(self.user)

        res = self.client.get(RECIPE_URL)
        recipes = models.Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, st.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
