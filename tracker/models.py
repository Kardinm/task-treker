from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg


PLAYER_TITLES = [
    (1, 'Новачок'),
    (3, 'Учень'),
    (5, 'Практикант'),
    (8, 'Знавець'),
    (12, 'Майстер'),
    (18, 'Ветеран'),
    (25, 'Грандмайстер'),
]


class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='playerprofile')
    total_xp = models.PositiveIntegerField(default=0)
    player_level = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=50, default='Новачок')


    def update_level(self):
        avg = Skill.objects.filter(user=self.user).aggregate(avg=Avg('level'))['avg']
        self.player_level = max(1, int(avg or 1))
        self.title = self._compute_title(self.player_level)
        self.save()


    def _compute_title(self, level):
        title = PLAYER_TITLES[0][1]
        for min_level, name in PLAYER_TITLES:
            if level >= min_level:
                title = name

        return title


    def __str__(self):
        return f'{self.user.username} profile'


class Skill(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=7, default='#6366f1')

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

    @property
    def completed_quests_count(self):
        return self.quests.filter(status='completed').count()

    def __str__(self):
        return f'{self.name} (Lv.{self.level})'

    class Meta:
        ordering = ['name']


class Quest(models.Model):
    RARITY_CHOICES = [
        ('common', 'Звичайний'),
        ('rare', 'Нічогенький'),
        ('epic', 'Напряжний'),
        ('legendary', 'Дуже напряжний'),
    ]
    STATUS_CHOICES = [
        ('pending', 'В очікуванні'),
        ('in_progress', 'В процесі'),
        ('completed', 'Виконано'),
        ('failed', 'Провалено'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Не треба'),
        ('medium', 'Бажано'),
        ('high', 'Треба'),
        ('critical', 'Або зараз, або ніколи'),
    ]
    XP_MULTIPLIER = {
        'common': 1, 'rare': 2, 'epic': 3, 'legendary': 5,
    }

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
    image = models.FileField(upload_to='quests/', blank=True, null=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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


class Note(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='notes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Note by {self.user.username} on "{self.quest}"'

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
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='bosses')
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

    @property
    def completed_quests_count(self):
        return Quest.objects.filter(user=self.user, skill=self.skill, status='completed').count()

    @property
    def quests_needed(self):
        current = self.skill.level
        needed_levels = max(0, self.min_level - current)
        return needed_levels * 2

    @property
    def quests_remaining(self):
        if self.is_ready:
            return 0
        needed_xp = 0
        for lvl in range(self.skill.level, self.min_level):
            needed_xp += 100 + (lvl - 1) * 50
        avg_xp = 25
        remaining = max(0, (needed_xp - self.skill.xp + avg_xp - 1) // avg_xp)
        return remaining

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['deadline']


class Item(models.Model):
    ITEM_TYPES = [
        ('focus', 'Концентрація'),
        ('recovery', 'Відновлення'),
        ('planning', 'Планування'),
        ('mindset', 'Мислення'),
    ]
    UNLOCK_LEVEL = [
        (1, 'Lv.1'), (3, 'Lv.3'), (5, 'Lv.5'),
        (8, 'Lv.8'), (12, 'Lv.12'),
    ]

    name = models.CharField(max_length=100)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    description = models.TextField()
    unlock_level = models.PositiveIntegerField(choices=UNLOCK_LEVEL, default=1)

    def is_unlocked_for(self, profile):
        return profile.player_level >= self.unlock_level

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['unlock_level', 'item_type', 'name']


class QuestItem(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='quest_items')
    item  = models.ForeignKey(Item, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('quest', 'item')