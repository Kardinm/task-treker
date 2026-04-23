from django.db import models
from accounts.models import PlayerProfile

class Item(models.Model):
    ITEM_TYPE = [
        ('boost','Буст'),
        ('focus','Фокус'),
        ('recovery','Відновлення стаміни'),
        ('shield','Захист від штрафу'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE)
    effect_value= models.FloatField(default=1.5)

    # ще щось добавити


class PlayerItem(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
