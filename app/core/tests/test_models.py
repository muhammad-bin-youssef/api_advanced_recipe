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
