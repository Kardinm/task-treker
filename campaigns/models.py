from django.db import models
from accounts.models import PlayerProfile
from skills.models import Skill

class Campaign(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)  
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # прогрес, нагорода

class Boss(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='bosses')
    title = models.CharField(max_length=200) 
    description = models.TextField(blank=True)
    deadline = models.DateTimeField()
    required_skill = models.ForeignKey(Skill, on_delete=models.SET_NULL, null=True)
    required_level = models.PositiveIntegerField(default=1) 
    is_defeated = models.BooleanField(default=False)


