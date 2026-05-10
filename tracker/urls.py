from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', views.DashboardView.as_view(), name='dashboard'),

    path('quests/', views.QuestListView.as_view(), name='quest_list'),
    path('quests/create/', views.QuestCreateView.as_view(), name='quest_create'),
    path('quests/<int:pk>/', views.QuestDetailView.as_view(), name='quest_detail'),
    path('quests/<int:pk>/edit/', views.QuestUpdateView.as_view(), name='quest_update'),
    path('quests/<int:pk>/delete/', views.QuestDeleteView.as_view(), name='quest_delete'),
    path('quests/<int:pk>/complete/', views.CompleteQuestView.as_view(), name='quest_complete'),

    path('quests/<int:quest_pk>/comment/', views.AddCommentView.as_view(), name='add_comment'),

    path('skills/', views.SkillListView.as_view(), name='skill_list'),
    path('skills/<int:pk>/', views.SkillDetailView.as_view(), name='skill_detail'),

    path('bosses/', views.BossListView.as_view(), name='boss_list'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)