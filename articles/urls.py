from django.urls import path
from rest_framework.routers import DefaultRouter
from articles.views import ArticleViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='articles')
router.register(r'categories', CategoryViewSet, basename='categories')

urlpatterns = router.urls
