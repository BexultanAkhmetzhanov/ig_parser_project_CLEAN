# locations/views.py

from rest_framework import generics, viewsets, permissions
from .models import Country, City
# --- ИЗМЕНЕНИЕ: Импортируем ОБА набора сериализаторов ---
from .serializers import CountryPublicSerializer, CityPublicSerializer, CountryAdminSerializer, CityAdminSerializer

# --- View для ПУБЛИЧНОГО API ---
class CountryListView(generics.ListAPIView):
    queryset = Country.objects.prefetch_related('cities').all()
    # <<< ИЗМЕНЕНИЕ: Используем ПУБЛИЧНЫЙ сериализатор >>>
    serializer_class = CountryPublicSerializer 
    permission_classes = [permissions.AllowAny] # Явно разрешаем доступ

# --- ViewSet'ы для АДМИН-ПАНЕЛИ (используют АДМИНСКИЕ сериализаторы) ---
class CountryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CountryAdminSerializer # <-- Используем админский
    queryset = Country.objects.prefetch_related('cities').all()

class CityViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CityAdminSerializer # <-- Используем админский
    queryset = City.objects.all()