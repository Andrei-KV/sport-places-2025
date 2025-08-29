from django.contrib import admin
from .models import Place, PendingPlace


admin.site.register(Place)

# Create a custom Admin class for the PendingPlace model
# Позволяет применять модерацию в один клик

# Главная идея: она говорит Django: "Эй, Django, когда ты будешь настраивать админ-панель, 
# пожалуйста, используй вот этот класс (PendingPlaceAdmin) для управления моделью PendingPlace."
# заменяет старую команду admin.site.register(PendingPlace, PendingPlaceAdmin).
@admin.register(PendingPlace)
class PendingPlaceAdmin(admin.ModelAdmin):

    # list_display: This tells Django which fields to show in the list view of the admin panel, 
    # making it easy to see all the relevant info at a glance.
    list_display = ('name', 'action', 'status', 'user', 'original_place')
    list_filter = ('status', 'action')
    # actions = ['approve_submission']: This adds a new option to the "Actions" dropdown menu in the admin panel.
    actions = ['approve_submission']

    @admin.action(description='Approve selected submissions')
    def approve_submission(self, request, queryset):
        for submission in queryset:
            if submission.action == 'add':
                Place.objects.create(name=submission.name, description=submission.description)
            elif submission.action == 'edit':
                original = submission.original_place
                original.name = submission.name
                original.description = submission.description
                original.save()
            # For 'delete' actions, the admin would likely delete the object from this list.
            
            submission.status = 'approved'
            submission.save()

        self.message_user(request, f"{queryset.count()} submissions have been approved.")
# approve_submission method: This function is the core of our moderation logic. 
# It loops through the selected submissions.
# If action is 'add', it creates a new Place object.
# If action is 'edit', it finds the original Place object and updates it.
# Finally, it sets the status of the PendingPlace submission to 'approved' and saves it.