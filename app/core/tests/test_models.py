from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core import models


def create_user(**kw):
    return get_user_model().objects.create_user(**kw)


class ModelTest(TestCase):
    def test_create_user_with_email_successful(self):
        email = "test@example.com"
        password = "password123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@EXAMPLE.com", "Test2@example.com"],
            ["TEST3@example.com", "TEST3@example.com"],
            ["test4@example.com", "test4@example.com"],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "password123")
            self.assertEqual(user.email, expected)

    def test_raise_value_error_no_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "password123")

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(
            "test@example.com", "password123"
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_recipe_success(self):
        user = create_user(
            name="testname",
            password="password1234",
            email="tsetemail@example.com",
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title="test_title_recipe",
            time_minutes=5,
            price=Decimal("5.50"),
            description="desc",
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        user = create_user(
            name="testname",
            password="password1234",
            email="testrecipe@example.com",
        )
        tag = models.Tag.objects.create(user=user, name="test tag")
        exists = models.Tag.objects.filter(user=user).exists()
        tag_db = models.Tag.objects.filter(user=user, name="test tag").first()
        self.assertTrue(exists)
        self.assertEqual(tag_db.name, tag.name)
        self.assertEqual(tag_db.user, tag.user)

    def test_create_ingredient(self):
        user = create_user(
            name="testname",
            password="password1234",
            email="testrecipe@example.com",
        )
        ingredient = models.Ingredient.objects.create(user=user, name="Ingrediente1")
        self.assertEqual(str(ingredient), ingredient.name)
