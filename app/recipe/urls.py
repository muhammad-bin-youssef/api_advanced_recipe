from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recipe import views


router = DefaultRouter()
router.register("", views.RecipeViewSet)

app_name = "recipe"

urlpatterns = [
    path("recipes", include(router.urls)),
]

# fa8b133b18281711297ae98faa0558d84e1f760a
