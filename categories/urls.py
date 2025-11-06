# categories/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryPublicViewSet

# Создаем роутер ТОЛЬКО для публичного API категорий
router = DefaultRouter()
router.register(r'categories', CategoryPublicViewSet, basename='public-categories')

urlpatterns = [
    # Подключаем роутер
    path('', include(router.urls)),
]