from django.db import models
from users.models import User  # Assuming the users app exists

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class UserTeam(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teams')  # Use a custom related_name
    teamadmin = models.BooleanField(default=False)

    class Meta:
        unique_together = ('team', 'user')  # Prevent duplicate entries

    def __str__(self):
        return f"{self.user.username} in {self.team.name}"
