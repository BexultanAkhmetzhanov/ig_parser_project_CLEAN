# categories/serializers.py

from rest_framework import serializers
from .models import Category, Subcategory

class SubcategoryAdminSerializer(serializers.ModelSerializer):
    """Сериализатор для управления Подкатегориями в админке."""
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category']

class CategoryAdminSerializer(serializers.ModelSerializer):
    """Сериализатор для Категории с вложенным списком её подкатегорий."""
    subcategories = SubcategoryAdminSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'subcategories']

class SubcategoryPublicSerializer(serializers.ModelSerializer):
    """
    Сериализатор для публичной информации о ПОДкатегории (только ID и имя).
    """
    class Meta:
        model = Subcategory
        fields = ['id', 'name']

class CategoryPublicSerializer(serializers.ModelSerializer):
    """
    Сериализатор для публичной Категории с вложенным списком 
    её публичных подкатегорий.
    """
    # Используем новый 'SubcategoryPublicSerializer'
    subcategories = SubcategoryPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        # Отдаем 'id', 'name' и вложенный список 'subcategories'
        fields = ['id', 'name', 'subcategories']