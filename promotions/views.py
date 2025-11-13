from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from .models import Promotion, Media
from .serializers import PromotionSerializer, PromotionUpdateSerializer, AdminPromotionCreateSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.management import call_command
from django.utils import timezone
import threading

from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from establishments.models import Establishment
import datetime

class PromotionListView(generics.ListAPIView):
    """
    API-представление для получения списка опубликованных акций.
    Поддерживает фильтрацию по ID города (параметр ?city=...).
    """
    serializer_class = PromotionSerializer

    def get_queryset(self):
        """
        Этот метод определяет, какие данные отдавать.
        Он переопределен для добавления фильтрации.
        """
        queryset = Promotion.objects.filter(status='published').order_by('-published_at')
        city_id = self.request.query_params.get('city')
        if city_id is not None:
            queryset = queryset.filter(establishment__city_id=city_id)
        
        return queryset
class PublishedListView(generics.ListAPIView):
    """
    API-представление для получения списка акций,
    которые уже ОПУБЛИКОВАНЫ. Доступно только администраторам.
    """
    serializer_class = PromotionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        """Отдает только акции со статусом 'published'."""
        # Мы также можем добавить фильтрацию по городу, как в PromotionListView
        queryset = Promotion.objects.filter(status='published').order_by('-published_at')
        city_id = self.request.query_params.get('city')
        if city_id is not None:
            queryset = queryset.filter(establishment__city_id=city_id)
        
        return queryset
class ModerationListView(generics.ListAPIView):
    """
    API-представление для получения списка акций,
    ожидающих модерации. Доступно только администраторам.
    """
    serializer_class = PromotionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        """Отдает только акции со статусом 'moderation'."""
        return Promotion.objects.filter(status='moderation').order_by('-created_at')


class ModerationDetailView(generics.RetrieveUpdateAPIView):
    """
    API-представление для получения и обновления одной конкретной акции.
    Доступно только администраторам.
    """
    permission_classes = [permissions.IsAdminUser]
    queryset = Promotion.objects.all()

    def get_serializer_class(self):
        """
        Возвращаем разные сериализаторы для GET и PUT запросов.
        """
        if self.request.method == 'GET':
            return PromotionSerializer
        return PromotionUpdateSerializer

    def update(self, request, *args, **kwargs):
        """
        Переопределяем метод update для лучшей обработки ошибок.
        """
        print(f"=== НАЧАЛО ОБРАБОТКИ PUT ЗАПРОСА ===")
        print(f"URL: {request.path}")
        print(f"Данные запроса: {request.data}")
        print(f"Заголовки: {dict(request.headers)}")
        
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            print(f"❌ Ошибка валидации: {e}")
            print(f"Детали ошибки: {e.detail}")
            raise
        except Exception as e:
            print(f"❌ Общая ошибка: {e}")
            raise

    def perform_update(self, serializer):
        """
        Переопределяем метод для добавления логики обновления published_at
        при изменении статуса на 'published'.
        """
        instance = serializer.instance
        old_status = instance.status
        
        print(f"=== ОБНОВЛЕНИЕ АКЦИИ {instance.id} ===")
        print(f"Старый статус: {old_status}")
        print(f"Новые данные: {serializer.validated_data}")
        print(f"Данные запроса: {self.request.data}")
        print(f"Метод запроса: {self.request.method}")
        
        # Сохраняем изменения
        try:
            serializer.save()
            print(f"✅ Акция успешно обновлена. Новый статус: {serializer.instance.status}")
        except Exception as e:
            print(f"❌ Ошибка при сохранении: {e}")
            raise
        
        # Если статус изменился на 'published', обновляем published_at
        if old_status != 'published' and serializer.instance.status == 'published':
            serializer.instance.published_at = timezone.now()
            serializer.instance.save(update_fields=['published_at'])
            print(f"Установлена дата публикации: {serializer.instance.published_at}")
        
        print(f"=== КОНЕЦ ОБНОВЛЕНИЯ ===\n")


class PromotionCreateView(APIView):
    """
    API-представление для ручного создания акции админом.
    Требует права админа и принимает multipart/form-data.
    """
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос для создания новой акции.
        """
        print(f"=== ПОЛУЧЕН ЗАПРОС НА СОЗДАНИЕ АКЦИИ ===")
        print(f"Данные: {request.data}")
        print(f"Файлы: {request.FILES}")

        # 1. Валидируем текстовые данные
        serializer = AdminPromotionCreateSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            print("✅ Валидация текстовых полей прошла успешно.")
        except ValidationError as e:
            print(f"❌ Ошибка валидации: {e.detail}")
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        establishment = validated_data['establishment']
        
        try:
            # 2. Создаем саму акцию
            new_promo = Promotion.objects.create(
                establishment=establishment,
                edited_text=validated_data['edited_text'],
                conditions=validated_data.get('conditions', ''),
                raw_text="Добавлено вручную администратором", # Заглушка
                status=Promotion.STATUS_PUBLISHED, # Сразу публикуем
                published_at=timezone.now() # Устанавливаем дату публикации
            )
            print(f"✅ Акция #{new_promo.id} создана в базе данных.")

            # 3. Обрабатываем и сохраняем медиафайлы
            uploaded_files = request.FILES.getlist('media')
            if not uploaded_files:
                # Если файлов нет, это не ошибка, просто возвращаем созданную акцию
                print("⚠️ Медиафайлы не были предоставлены.")
                # Сериализуем созданный объект для ответа
                result_serializer = PromotionSerializer(new_promo)
                return Response(result_serializer.data, status=status.HTTP_201_CREATED)
            
            print(f"Начинаю обработку {len(uploaded_files)} медиафайлов...")

            # Создаем путь для сохранения, похожий на тот, что в парсере
            today_str = datetime.datetime.now().strftime('%Y-%m-%d')
            username_safe = establishment.instagram_url.strip('/').split('/')[-1]
            base_folder_path = (
                f"{establishment.city.country.name}/{establishment.city.name}/"
                f"{username_safe}/{today_str}/Manually_Added"
            )

            for file in uploaded_files:
                file_type_string = 'video' if 'video' in file.content_type else 'image'
                
                # Генерируем уникальное имя файла для хранилища
                # (Включаем ID акции, чтобы избежать конфликтов)
                file_save_path = f"{base_folder_path}/promo_{new_promo.id}_{file.name}"
                
                # 4. Сохраняем файл в облачное хранилище (S3/R2 и т.д.)
                try:
                    saved_path = default_storage.save(file_save_path, file)
                    print(f"  ...Файл '{file.name}' сохранен в хранилище по пути: {saved_path}")

                    # 5. Создаем запись Media в базе данных
                    Media.objects.create(
                        promotion=new_promo,
                        file_path=saved_path, # Используем путь, который вернуло хранилище
                        file_type=file_type_string
                    )
                except Exception as e:
                    # Если один из файлов не сохранился, это проблема.
                    # Мы удалим уже созданную акцию, чтобы не было "мусора".
                    new_promo.delete()
                    print(f"❌ Ошибка при сохранении файла '{file.name}': {e}")
                    return Response(
                        {"error": f"Ошибка при сохранении файла: {e}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            print(f"✅ Все {len(uploaded_files)} файлов успешно сохранены и привязаны к акции.")
            
            # 6. Возвращаем созданную акцию со всеми медиа
            result_serializer = PromotionSerializer(new_promo)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"❌ Непредвиденная ошибка при создании акции: {e}")
            return Response(
                {"error": f"Внутренняя ошибка сервера: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TriggerParseView(APIView):
    """
    API-представление для запуска парсера вручную.
    Доступно только администраторам.
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        """
        Принимает POST-запрос и запускает команду парсинга в отдельном потоке.
        """
        def run_command_in_thread():
            # Эта функция будет выполняться в фоновом режиме,
            # чтобы не заставлять пользователя ждать завершения парсинга.
            print("Запуск парсинга из API...")
            call_command('parse_instagram')
            print("Парсинг из API завершен.")

        # Запускаем команду в отдельном потоке
        thread = threading.Thread(target=run_command_in_thread)
        thread.start()

        # Сразу же отвечаем пользователю, что задача принята
        return Response(
            {"message": "Процесс парсинга запущен в фоновом режиме. Результаты появятся в разделе модерации через несколько минут."},
            status=status.HTTP_202_ACCEPTED
        )