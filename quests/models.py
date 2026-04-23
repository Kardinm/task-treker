from django.db import models
from accounts.models import PlayerProfile
from skills.models import Skill
from campaigns.models import Campaign

class Quest(models.Model):
    DIFFICULTY = [
        ('common','Common'),
        ('uncommon','Uncommon'),
        ('rare','Rare'),
        ('epic','Epic'),
        ('legendary','Legendary'),
    ]

    STATUS = [
        ('active','Активне'),
        ('done','Виконане'),
        ('failed','Провалене'),
        ('postponed','Відкладене'),
    ]

    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.SET_NULL, null=True)
    campaign = models.ForeignKey(Campaign, null=True, blank=True, on_delete=models.SET_NULL)

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY, default='common')
    status = models.CharField(max_length=10, choices=STATUS, default='active')
    xp_reward = models.PositiveIntegerField(default=10)
    deadline = models.DateTimeField(null=True, blank=True)
    has_penalty = models.BooleanField(default=False)
    penalty_xp = models.IntegerField(default=0) 
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # повторюваність, Boss
