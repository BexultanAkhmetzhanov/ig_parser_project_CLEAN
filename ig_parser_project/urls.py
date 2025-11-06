# ig_parser_project/urls.py

from django.urls import path, include
from establishments.admin import site as custom_admin_site
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter

# Импортируем все наши ViewSet'ы
from establishments.views import EstablishmentViewSet
from locations.views import CountryViewSet, CityViewSet
from categories.views import CategoryViewSet, SubcategoryViewSet, CategoryWithSubcategoriesView, CategoryPublicViewSet

from django.conf import settings
from django.conf.urls.static import static


from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.management import call_command
import threading
from django.views.generic import RedirectView

# Создаем роутер для админ-панели
router = DefaultRouter()
router.register(r'establishments', EstablishmentViewSet, basename='establishment')
router.register(r'countries', CountryViewSet, basename='country')
router.register(r'cities', CityViewSet, basename='city')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'subcategories', SubcategoryViewSet, basename='subcategory')

public_router = DefaultRouter()
#public_router.register(r'locations', CountryListView, basename='locations')
# ✅ 3. ЗАРЕГИСТРИРУЙ НОВЫЙ VIEWSET
#public_router.register(r'categories', CategoryPublicViewSet, basename='public-categories')

urlpatterns = [
    path('', RedirectView.as_view(url='https://promotionseverywhere.netlify.app/', permanent=False)), 
    #path('', RedirectView.as_view(url='http://127.0.0.1:8000/', permanent=False)), 
    path('admin/', custom_admin_site.urls),
    
    # --- Публичные API ---
    path('api/', include('promotions.urls')), # (уже было)
    path('api/', include('locations.urls')),
    
    path('api/', include('categories.urls')),

    # --- API для аутентификации ---
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- Защищенные API для React-админки ---
    path('api/admin/', include(router.urls)),
    # Старый URL для получения категорий с подкатегориями (для формы парсинга)
    path('api/admin/categories-with-subcategories/', CategoryWithSubcategoriesView.as_view(), name='categories-subcategories'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)