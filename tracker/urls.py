from django.urls import path


urlpatterns = [
    path('', name='profile'),
    path('quests/', name='quests'),
    path('quest/<quest_title>/complete/', name='complete_quest'),
    path('skills/', name='skills'),
]