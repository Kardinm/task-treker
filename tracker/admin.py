from django.contrib import admin
from .models import Quest, Skill, PlayerProfile, Note, Boss, Item


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'skill', 'status', 'priority', 'deadline']
    list_filter = ['status', 'priority', 'rarity']
    search_fields = ['title', 'user__username']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'level', 'xp']


@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'player_level', 'total_xp', 'title']


@admin.register(Boss)
class BossAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'skill', 'min_level', 'deadline', 'status']

admin.site.register(Note)
admin.site.register(Item)
