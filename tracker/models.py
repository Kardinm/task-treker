from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg

class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='playerprofile')
    total_xp = models.PositiveIntegerField(default=0)
    player_level = models.PositiveIntegerField(default=1)
    stamina = models.PositiveIntegerField(default=100)
    title = models.CharField(max_length=50, default='Новачок')

    def update_level(self):
        avg = Skill.objects.filter(user=self.user).aggregate(avg=Avg('level'))['avg']
        self.player_level = max(1, int(avg or 1))
        self.save()

    def __str__(self):
        return f'{self.user.username} profile'
    

class Skill(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=7, default='#007bff')

    def add_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
        self.save()

    @property
    def xp_to_next_level(self):
        return 100 + (self.level - 1) * 50

    @property
    def xp_percent(self):
        return int((self.xp / self.xp_to_next_level) * 100)

    def __str__(self):
        return f'{self.name} (Lv.{self.level})'

    class Meta:
        ordering = ['name']


class Quest(models.Model):
    RARITY_CHOICES = [
        ('common', 'Common'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ]
    STATUS_CHOICES = [
        ('pending', 'В очікуванні'),
        ('in_progress', 'В процесі'),
        ('completed', 'Виконано'),
        ('failed', 'Провалено'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Низький'),
        ('medium', 'Середній'),
        ('high', 'Високий'),
        ('critical', 'Критичний'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quests')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='quests')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default='common')
    deadline = models.DateTimeField(null=True, blank=True)
    xp_reward = models.PositiveIntegerField(default=10)
    penalty_xp = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.FileField(upload_to='quests/', blank=True, null=True)

    XP_MULTIPLIER = {
        'common': 1,
        'rare': 2,
        'epic': 3,
        'legendary': 5,
    }

    @property
    def calculate_xp(self):
        return self.xp_reward * self.XP_MULTIPLIER.get(self.rarity, 1)

    @property
    def is_overdue(self):
        if self.deadline and self.status != 'completed':
            return timezone.now() > self.deadline
        return False

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Comment(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.quest}'

    class Meta:
        ordering = ['-created_at']


class Boss(models.Model):
    STATUS_CHOICES = [
        ('preparing', 'Готується'),
        ('defeated', 'Переможено'),
        ('lost', 'Поразка'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bosses')
    name = models.CharField(max_length=200)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    min_level = models.PositiveIntegerField(default=1)
    deadline = models.DateTimeField()
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='preparing')
    reward_xp = models.PositiveIntegerField(default=100)

    @property
    def is_ready(self):
        return self.skill.level >= self.min_level

    @property
    def days_left(self):
        diff = self.deadline - timezone.now()
        return max(0, diff.days)

    @property
    def level_progress_percent(self):
        if self.min_level == 0:
            return 100
        return min(100, int((self.skill.level / self.min_level) * 100))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['deadline']


class Item(models.Model):
    ITEM_TYPES = [
        ('xp_boost', 'Буст XP'),
        ('stamina', 'Відновлення енергії'),
        ('shield', 'Захист від штрафу'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    effect_value = models.PositiveIntegerField(default=10)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.name} x{self.quantity}'