from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class Team(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, name, password=None, **extra_fields):
        if not name:
            raise ValueError("The Name field must be set")
        user = self.model(name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, password=None, **extra_fields):
        extra_fields.setdefault("admin", True)
        return self.create_user(name, password, **extra_fields)


class Username(AbstractBaseUser):
    name = models.TextField(unique=True)
    email = models.TextField(null=True, blank=True)
    phone = models.BigIntegerField(null=True, blank=True)
    logged_in = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "name"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.admin


class UsernameTeam(models.Model):
    username = models.ForeignKey(Username, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    team_admin = models.BooleanField()

    def __str__(self):
        return f"{self.username.name} - {self.team.name}"


class TicketStatusType(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class AffectedEquipment(models.Model):
    ticket = models.BigIntegerField()
    equipment = models.BigIntegerField()

    def __str__(self):
        return f"Ticket: {self.ticket} - Equipment: {self.equipment}"

