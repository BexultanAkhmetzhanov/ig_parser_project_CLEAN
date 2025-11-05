from rest_framework import viewsets, permissions
from .models import Establishment
from .serializers import EstablishmentAdminSerializer

class EstablishmentViewSet(viewsets.ModelViewSet):
    serializer_class = EstablishmentAdminSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = Establishment.objects.select_related('city', 'subcategory').all()
        city_id = self.request.query_params.get('city')
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        return queryset