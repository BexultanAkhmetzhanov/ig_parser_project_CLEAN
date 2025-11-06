# categories/views.py

from rest_framework import generics, viewsets, permissions
from .models import Category, Subcategory
from .serializers import CategoryAdminSerializer, SubcategoryAdminSerializer, CategoryPublicSerializer

# --- View для админки (получение категорий с подкатегориями) ---
class CategoryWithSubcategoriesView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CategoryAdminSerializer
    queryset = Category.objects.prefetch_related('subcategories').all()

# --- Новые ViewSet'ы для админ-панели ---
class CategoryViewSet(viewsets.ModelViewSet):
    """API для CRUD-операций с Категориями."""
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CategoryAdminSerializer
    queryset = Category.objects.prefetch_related('subcategories').all()

class SubcategoryViewSet(viewsets.ModelViewSet):
    """API для CRUD-операций с Подкатегориями."""
    permission_classes = [permissions.IsAdminUser]
    serializer_class = SubcategoryAdminSerializer
    queryset = Subcategory.objects.all()

class CategoryPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Публичный ViewSet (только для чтения) для получения списка
    Категорий с вложенными Подкатегориями.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = CategoryPublicSerializer
    
    # ВАЖНО: Оптимизация (как и в админке), 
    # чтобы избежать N+1 запросов к базе данных.
    queryset = Category.objects.prefetch_related('subcategories').all()