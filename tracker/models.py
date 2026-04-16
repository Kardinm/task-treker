from django.db import models
from django.contrib.auth.models import User


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    xp = models.IntegerField(default=0)
    xp_to_next = models.IntegerField(default=50)
    stamina = models.IntegerField(default=100) 
    

class Skill(models.Model):
    SKILL_TYPES = [
        ('PY', 'Python')
        ('ENG', 'English')
        ('MA', 'Math')
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    skill_type = models.CharField(max_length=10, choices=SKILL_TYPES)
    

class Quest(models.Model):
    DIFFICULTY = [
        (1, 'Easy')
        (2, 'Medium')
        (3, 'Hard')
        (5, 'Boss')
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    xp_reward = models.IntegerField(default=10)
    difficulty = models.IntegerField(choices=DIFFICULTY, default=1)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    deadline = models.DateTimeField(null=True, blank=True)
    
 