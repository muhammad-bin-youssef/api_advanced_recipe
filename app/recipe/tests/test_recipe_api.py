from decimal import Decimal
from core import models
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status as st
from rest_framework.test import APIClient
from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse("recipe:recipe-list")


def get_recipe_url(id):
    return reverse("recipe:recipe-detail", args=[id])


def create_recipe(user, **kw):
    payload = {
        "title": "test recipe",
        "time_minutes": 5,
        "description": "test desc",
        "price": Decimal("5.5"),
        "link": "test link",
    }
    payload.update(kw)
    recipe = models.Recipe.objects.create(user=user, **payload)
    return recipe


def create_user(**kw):
    return get_user_model().objects.create_user(**kw)


class PublicRecipeTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_requiered_fail(self):
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, st.HTTP_401_UNAUTHORIZED)


class PrivateRecipeTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(
            email="testrecipe@exaple.com",
            password="password1234",
        )
        self.client.force_authenticate(self.user)

    def test_retrive_recipe(self):
        create_recipe(user=self.user)
        create_recipe(user=self.user)

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
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipes = models.Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, st.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe_success(self):
        payload = {
            "title": "Sample recipe",
            "time_minutes": 30,
            "price": Decimal("5.99"),
        }
        res = self.client.post(RECIPE_URL, payload)
        recipe = models.Recipe.objects.filter(id=res.data["id"]).exists()
        self.assertEqual(res.status_code, st.HTTP_201_CREATED)
        self.assertTrue(recipe)

    def test_partial_update_recipe(self):
        recipe = create_recipe(user=self.user)
        payload = {
            "title": "test update recipe",
        }
        url = get_recipe_url(recipe.id)
        res = self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(res.status_code, st.HTTP_200_OK)
        self.assertEqual(res.data["link"], recipe.link)
        self.assertEqual(res.data["title"], recipe.title)
        self.assertEqual(self.user, recipe.user)
