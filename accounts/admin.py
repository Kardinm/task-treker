from django.contrib import admin
from .models import PlayerProfile


@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_xp', 'stamina', 'created_at')
    search_fields = ('user__username',)
