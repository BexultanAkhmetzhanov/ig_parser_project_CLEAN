# locations/serializers.py

from rest_framework import serializers
from .models import Country, City

# --- Сериализаторы для ПУБЛИЧНОГО API (/api/locations/) ---

class CityPublicSerializer(serializers.ModelSerializer):
    """Простой сериализатор Города для публичного API (только ID и имя)."""
    class Meta:
        model = City
        fields = ['id', 'name']

class CountryPublicSerializer(serializers.ModelSerializer):
    """Сериализатор Страны для публичного API с вложенными городами."""
    # Используем CityPublicSerializer
    cities = CityPublicSerializer(many=True, read_only=True) 

    class Meta:
        model = Country
        fields = ['id', 'name', 'cities']


# --- Сериализаторы для АДМИНКИ (/api/admin/...) ---

class CityAdminSerializer(serializers.ModelSerializer):
    """Сериализатор для управления Городами в админке (включает ID страны)."""
    class Meta:
        model = City
        fields = ['id', 'name', 'country'] # <-- Оставляем 'country' для админки

class CountryAdminSerializer(serializers.ModelSerializer):
    """Сериализатор для управления Странами в админке."""
    # Можно оставить вложенные города для просмотра, но они не будут редактироваться через этот эндпоинт
    cities = CityPublicSerializer(many=True, read_only=True) 

    class Meta:
        model = Country
        fields = ['id', 'name', 'cities']