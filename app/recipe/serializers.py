from rest_framework import serializers
from core import models


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = models.Recipe
        fields = [
            "user_id",
            "id",
            "title",
            "time_minutes",
            "price",
            "link",
            "tags",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        recipe = models.Recipe.objects.create(**validated_data)
        auth_user = self.context["request"].user
        for tag in tags:
            tag_obj, created = models.Recipe.objects.get_or_create(auth_user, **tag)
            recipe.tags.add(tag_obj)
        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description"]
