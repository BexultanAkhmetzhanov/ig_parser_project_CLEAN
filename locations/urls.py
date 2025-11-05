from django.urls import path
from .views import CountryListView

urlpatterns = [
    path('locations/', CountryListView.as_view(), name='country-list'),
]