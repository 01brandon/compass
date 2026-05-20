from rest_framework import serializers
from articles.models import Article, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ArticleSerializer(serializers.ModelSerializer):

    author_name = serializers.CharField(
        source="author.full_name",
        read_only=True
    )

    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )

    class Meta:
        model = Article

        fields = [
            "id",
            "author",
            "author_name",
            "category",
            "category_name",
            "title",
            "slug",
            "featured_image",
            "excerpt",
            "content",
            "view_count",
            "is_featured",
            "status",
            "published_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "author",
            "view_count",
            "published_at",
            "created_at",
            "updated_at",
        ]