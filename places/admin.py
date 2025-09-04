from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from .models import Place, PendingPlace, Photo, Category


class PhotoInline(admin.TabularInline):
    """
    Класс для отображения фотографий в виде таблицы
    на странице редактирования PendingPlace.
    """
    model = Photo
    extra = 0  # Не добавляем пустые формы по умолчанию
    fields = ('image',)
    readonly_fields = ('image',)
    # Определяем, как будут отображаться фото в списке
    def image_tag(self, obj):
        from django.utils.html import format_html
        return format_html('<img src="{}" style="height: 100px; width: auto;" />'.format(obj.image.url))

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['category', 'name', 'user']
    list_filter = ['category']
    list_display_links = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(PendingPlace)
class PendingPlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'action', 'status', 'user', 'original_place')
    list_filter = ('status', 'action')
    actions = ['approve_submission']
    
    # Добавляем PhotoInline для отображения фото
    inlines = [PhotoInline]

    # Определяем поля для отображения на странице деталей
    # photo_inline автоматически добавится благодаря inlines
    fieldsets = (
        ('Детали заявки', {
            'fields': ('name', 'description', 'category', 'latitude', 'longitude', 'action', 'status', 'user', 'original_place'),
        }),
    )

    
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/approve/', self.admin_site.admin_view(self.approve_single_submission), name='places_pendingplace_approve'),
        ]
        return custom_urls + urls

    def approve_single_submission(self, request, object_id):
        submission = self.get_object(request, object_id)
        if submission.action == 'add':
            new_place = Place.objects.create(
                name=submission.name,
                description=submission.description,
                user=submission.user,
                latitude=submission.latitude,
                longitude=submission.longitude,
                category=submission.category,
            )
            photos_to_copy = Photo.objects.filter(pending_place=submission)
            photos_to_copy.update(pending_place=None, place=new_place)

        elif submission.action == 'edit':
            original = submission.original_place
            original.description = submission.description
            original.save()
            
            photos_to_copy = Photo.objects.filter(pending_place=submission)
            photos_to_copy.update(pending_place=None, place=original)
        
        # Обновляем статус заявки на "одобрена"
        submission.status = 'approved'
        submission.save()

        self.message_user(request, f"Заявка '{submission.name}' была одобрена.")
        
        return HttpResponseRedirect("../")

    @admin.action(description='Одобрить выбранные заявки')
    def approve_submission(self, request, queryset):
        for submission in queryset:
            if submission.action == 'add':
                new_place = Place.objects.create(
                    name=submission.name,
                    description=submission.description,
                    user=submission.user,
                    latitude=submission.latitude,
                    longitude=submission.longitude,
                    category=submission.category,
                )
                photos_to_copy = Photo.objects.filter(pending_place=submission)
                photos_to_copy.update(pending_place=None, place=new_place)

            elif submission.action == 'edit':
                original = submission.original_place
                original.description = submission.description
                original.save()
                
                photos_to_copy = Photo.objects.filter(pending_place=submission)
                photos_to_copy.update(pending_place=None, place=original)
            
            submission.status = 'approved'
            submission.save()

        self.message_user(request, f"{queryset.count()} submissions have been approved.")


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('image', 'pending_place', 'place')
    list_filter = ('pending_place', 'place')