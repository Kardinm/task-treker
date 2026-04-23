from django.db import models
from django.contrib.auth.models import User

class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_xp = models.PositiveIntegerField(default=0)
    stamina = models.PositiveIntegerField(default=100) 
    created_at = models.DateTimeField(auto_now_add=True)

    # title, ачівки
