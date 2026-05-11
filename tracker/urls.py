from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', views.DashboardView.as_view(), name='dashboard'),

    path('quests/', views.QuestListView.as_view(), name='quest_list'),
    path('quests/create/', views.QuestCreateView.as_view(), name='quest_create'),
    path('quests/<int:pk>/', views.QuestDetailView.as_view(), name='quest_detail'),
    path('quests/<int:pk>/edit/', views.QuestUpdateView.as_view(), name='quest_update'),
    path('quests/<int:pk>/delete/', views.QuestDeleteView.as_view(), name='quest_delete'),
    path('quests/<int:pk>/complete/', views.CompleteQuestView.as_view(), name='quest_complete'),

    path('quests/<int:quest_pk>/notes/', views.AddNoteView.as_view(), name='add_note'),
    path('quests/<int:quest_pk>/notes/<int:pk>/delete/', views.DeleteNoteView.as_view(), name='delete_note'),

    path('quests/<int:quest_pk>/items/<int:item_pk>/add/', views.AddItemToQuestView.as_view(), name='add_item_to_quest'),
    path('quests/<int:quest_pk>/items/<int:item_pk>/remove/', views.RemoveItemFromQuestView.as_view(), name='remove_item_from_quest'),

    path('skills/', views.SkillListView.as_view(), name='skill_list'),
    path('skills/<int:pk>/', views.SkillDetailView.as_view(), name='skill_detail'),
    path('skills/create/', views.SkillCreateView.as_view(), name='skill_create'),
    path('skills/<int:pk>/delete/', views.SkillDeleteView.as_view(), name='skill_delete'),

    path('bosses/', views.BossListView.as_view(), name='boss_list'),
    path('bosses/create/', views.BossCreateView.as_view(), name='boss_create'),
    path('bosses/<int:pk>/edit/', views.BossUpdateView.as_view(), name='boss_update'),
    path('bosses/<int:pk>/delete/', views.BossDeleteView.as_view(), name='boss_delete'),
    path('bosses/<int:pk>/fight/', views.BossFightView.as_view(), name='boss_fight'),

    path('inventory/', views.InventoryView.as_view(), name='inventory'),

    path('help/', views.HelpView.as_view(), name='help'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)