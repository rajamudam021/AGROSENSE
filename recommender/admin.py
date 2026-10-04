from django.contrib import admin
from .models import UserProfile, Prediction


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'phone')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')
    list_per_page = 25


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display   = (
        'user', 'predicted_label', 'N', 'P', 'K',
        'temperature', 'humidity', 'ph', 'rainfall',
        'soil_health_score', 'city', 'created_at',
    )
    list_filter    = ('predicted_label', 'created_at')
    search_fields  = ('user__username', 'predicted_label', 'city')
    readonly_fields = ('created_at',)
    ordering       = ('-created_at',)
    list_per_page  = 25
