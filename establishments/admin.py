# establishments/admin.py

from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.db.models import Count, Q
from django.utils import timezone
from django.conf import settings # <-- Убедитесь, что этот импорт есть

# Импортируем все наши модели
from .models import Establishment
from locations.models import Country, City
from categories.models import Category, Subcategory
from promotions.models import Promotion, Media

class CustomAdminSite(admin.AdminSite):
    """Наша кастомная админка с дополнительными страницами."""

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('moderation/', self.admin_view(self.moderation_view), name='moderation'),
            path('moderation/category/<int:category_id>/', self.admin_view(self.moderation_category_view), name='moderation_category'),
            path('moderation/promotion/<int:promo_id>/edit/', self.admin_view(self.moderation_promo_edit_view), name='moderation_promo_edit'),
        ]
        return custom_urls + urls

    def moderation_view(self, request):
        """View для главного дашборда модерации."""
        categories_with_counts = Category.objects.annotate(
            new_promotions_count=Count(
                'subcategories__establishments__promotions',
                filter=Q(subcategories__establishments__promotions__status='moderation')
            )
        ).order_by('-new_promotions_count', 'name')

        context = {
            **self.each_context(request),
            'title': 'Модерация акций',
            'categories': categories_with_counts,
        }
        return render(request, 'admin/moderation_list.html', context)

    def moderation_category_view(self, request, category_id):
        """View для отображения списка акций в выбранной категории."""
        category = Category.objects.get(pk=category_id)
        promotions = Promotion.objects.filter(
            status='moderation',
            establishment__subcategory__category=category
        ).select_related('establishment')

        context = {
            **self.each_context(request),
            'title': f'Акции в категории: {category.name}',
            'category': category,
            'promotions': promotions,
        }
        return render(request, 'admin/moderation_detail.html', context)

    def moderation_promo_edit_view(self, request, promo_id):
        """View для редактирования и публикации акции."""
        promo = Promotion.objects.select_related('establishment').get(pk=promo_id)

        # Обработка сохранения формы
        if request.method == 'POST':
            promo.edited_text = request.POST.get('edited_text', '')
            promo.conditions = request.POST.get('conditions', '')
            promo.status = 'published'
            promo.published_at = timezone.now()
            promo.save()

            category_id = promo.establishment.subcategory.category_id
            return redirect('admin:moderation_category', category_id=category_id)

        # Отображение формы
        context = {
            **self.each_context(request),
            'title': f'Редактирование акции от "{promo.establishment.name}"',
            'promo': promo,
            'MEDIA_URL': settings.MEDIA_URL, # <-- ДОБАВЛЯЕМ MEDIA_URL В КОНТЕКСТ
        }
        return render(request, 'admin/moderation_form.html', context)

# Создаем один экземпляр нашей кастомной админки
site = CustomAdminSite()

# Регистрируем все наши модели в этой кастомной админке
site.register(Establishment)
site.register(Country)
site.register(City)
site.register(Category)
site.register(Subcategory)
site.register(Promotion)
site.register(Media)