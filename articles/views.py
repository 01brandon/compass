from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
# from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from articles.permissions import ArticlePermission
from django.utils import timezone

from articles.models import Article, Category
from articles.serializers import ArticleSerializer, CategorySerializer

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.select_related('author', 'category').all()
    serializer_class = ArticleSerializer
    permission_classes = [ArticlePermission]
    
    lookup_field = 'slug'  # Use slug for lookup instead of ID
    filterset_fields = [
        'status', 
        'category_name', 
        'author_name', 
        'is_featured'
    ]  
    
    search_fields = ['title', 'excerpt', 'content']
    ordering_fields = ['published_at', 'created_at', 'view_count']
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        
    @action(detail=True, methods=['post'])
    def publish(self, request, slug=None):
        article = self.get_object()
        if request.user.role not in ['admin', 'editor', 'superadmin']:
            return Response({'detail': 'You do not have permission to publish this article.'}, status=status.HTTP_403_FORBIDDEN)
        if article.status != Article.Status.PUBLISHED:
            article.status = Article.Status.PUBLISHED
            article.published_at = timezone.now()
            article.save()
            serializer = self.get_serializer(article)
            return Response({'detail': 'Article published successfully.'})
        return Response(serializer.data | {'detail': 'Article is already published.'}, status=status.HTTP_400_BAD_REQUEST)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

def index(request):
    return HttpResponse("Welcome to the News API!")

