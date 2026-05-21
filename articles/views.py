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
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiExample


@extend_schema_view(
    list=extend_schema(
       tags=['Articles'],
       summary='List all articles',
        description='Retrieve a list of all articles. Supports filtering, searching, and ordering.',
    ),
    retrieve=extend_schema(
        tags=['Articles'],
        summary='Retrieve an article',
        description='Get the details of a specific article by its slug.',
    ),
    create=extend_schema(
        tags=['Articles'],
        summary='Create a new article',
        description='Create a new article. Requires authentication and appropriate permissions.',
    ),
    update=extend_schema(
        tags=['Articles'],
        summary='Update an article',
        description='Update an existing article. Requires authentication and appropriate permissions.',
    ),
    partial_update=extend_schema(
        tags=['Articles'],
        summary='Partially update an article',
        description='Partially update an existing article. Requires authentication and appropriate permissions.',
    ),
    destroy=extend_schema(
        tags=['Articles'],
        summary='Delete an article',
        description='Delete an existing article. Requires authentication and appropriate permissions.', 
    ),
    
    publish=extend_schema(
        summary='Publish an article',
        description='Publish a draft article. Only users with admin, editor, or superadmin roles can publish articles.',
    ),
    unpublish=extend_schema(
        summary='Unpublish an article',
        description='Unpublish a published article. Only users with admin, editor, or superadmin roles can unpublish articles.',
    )
    
)

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
        
@extend_schema_view(
    list=extend_schema(
       tags=['Categories'],
       summary='List all categories',
        description='Retrieve a list of all categories.',
    ),
    retrieve=extend_schema(
        tags=['Categories'],
        summary='Retrieve a category',
        description='Get the details of a specific category by its slug.',
    ),
    create=extend_schema(
        tags=['Categories'],
        summary='Create a new category',
        description='Create a new category. Requires authentication and appropriate permissions.',
    ),
    update=extend_schema(
        tags=['Categories'],
        summary='Update a category',
        description='Update an existing category. Requires authentication and appropriate permissions.',
    ),
    partial_update=extend_schema(
        tags=['Categories'],
        summary='Partially update a category',
        description='Partially update an existing category. Requires authentication and appropriate permissions.',
    ),
    destroy=extend_schema(
        tags=['Categories'],
        summary='Delete a category',
        description='Delete an existing category. Requires authentication and appropriate permissions.', 
    )
)
class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ArticlePermission]

    lookup_field = 'slug'