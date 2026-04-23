from django.db import models
from accounts.models import PlayerProfile

class Skill(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100) 
    current_xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)

    # xp_to_next_level()
