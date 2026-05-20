from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from articles.models import Article, Category
from articles.serializers import ArticleSerializer, CategorySerializer
from articles.permissions import ArticlePermission

class ArticleViewSet(viewsets.ModelViewSet):

    queryset = Article.objects.select_related(
        'author',
        'category'
    ).all()

    serializer_class = ArticleSerializer
    permission_classes = [ArticlePermission]

    lookup_field = 'slug'

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    filterset_fields = [
        'status',
        'category',
        'is_featured'
    ]

    search_fields = [
        'title',
        'excerpt',
        'content'
    ]

    ordering_fields = [
        'published_at',
        'created_at',
        'view_count'
    ]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        
    @action(detail=True, methods=['post'])
    def publish(self, request, slug=None):

        article = self.get_object()

        if request.user.role not in [
            'admin',
            'editor',
            'superadmin'
        ]:
            return Response(
                {'detail': 'Not allowed to publish'},
                status=status.HTTP_403_FORBIDDEN
            )

        if article.status == Article.Status.PUBLISHED:
            return Response(
                {'detail': 'Article already published'},
                status=status.HTTP_400_BAD_REQUEST
            )

        article.status = Article.Status.PUBLISHED
        article.published_at = timezone.now()
        article.save()

        serializer = self.get_serializer(article)

        return Response({
            'detail': 'Article published successfully',
            'article': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def unpublish(self, request, slug=None):

        article = self.get_object()

        if request.user.role not in [
            'admin',
            'editor',
            'superadmin'
        ]:
            return Response(
                {'detail': 'Not allowed to unpublish'},
                status=status.HTTP_403_FORBIDDEN
            )

        if article.status != Article.Status.PUBLISHED:
            return Response(
                {'detail': 'Article is not published'},
                status=status.HTTP_400_BAD_REQUEST
            )

        article.status = Article.Status.DRAFT
        article.published_at = None
        article.save()

        serializer = self.get_serializer(article)

        return Response({
            'detail': 'Article unpublished successfully',
            'article': serializer.data
        })
        
    
class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ArticlePermission]

    lookup_field = 'slug'