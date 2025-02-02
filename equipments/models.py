from django.db import models
from teams.models import Team  

class Site(models.Model):

    name = models.CharField(max_length=200)
    additional_info = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class EquipmentType(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Equipment Type"
        verbose_name_plural = "Equipment Types"

    def __str__(self):
        return self.name


class Equipment(models.Model):
    name = models.CharField(max_length=200)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="equipment")  
    type = models.ForeignKey(EquipmentType, on_delete=models.CASCADE)
    last_change_ticket = models.BigIntegerField(null=True, blank=True)
    first_level_support_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="first_level_support")
    second_level_support_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="second_level_support")
    additional_info = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
