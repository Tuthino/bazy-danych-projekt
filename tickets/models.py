from django.db import models
from django.contrib.auth import get_user_model
from teams.models import Team 
from users.models import User
from equipments.models import Equipment, EquipmentType


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class TicketType(models.Model):
    name = models.TextField()

    class Meta:
        verbose_name = "Ticket Type"
        verbose_name_plural = "Ticket Types"

    def __str__(self):
        return self.name


class TicketStatusType(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class Ticket(models.Model):
    type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  
    owner_team = models.ForeignKey(Team, on_delete=models.CASCADE)
    status = models.ForeignKey(TicketStatusType, on_delete=models.CASCADE)
    issue_started = models.DateTimeField()
    issue_resolved = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ticket #{self.id} ({self.type.name})"


class Comment(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')  
    comment_text = models.TextField()
    comment_type = models.ForeignKey('CommentType', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on Ticket #{self.ticket.id}"
class CommentType(models.Model):
    name = models.TextField()

    class Meta:
        verbose_name = "Comment Type"
        verbose_name_plural = "Comment Types"

    def __str__(self):
        return self.name

class TicketAcknowledgmentStatus(models.Model):
    """Lookup table for acknowledgment statuses."""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Acknowledgment Status"
        verbose_name_plural = "Acknowledgment Statuses"


class TicketRequestedTeam(models.Model):
    """Tracks teams requested for ticket collaboration."""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="requested_teams")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="requested_tickets")
    status = models.ForeignKey(TicketAcknowledgmentStatus, on_delete=models.CASCADE)

    def __str__(self):
        return f"Team {self.team.name} - Ticket #{self.ticket.id}"

    class Meta:
        verbose_name = "Requested Team"
        verbose_name_plural = "Requested Teams"

class TicketsAffectedEquipment(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        db_column='ticket_id'
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        db_column='equipment_id'
    )

    class Meta:
        verbose_name = "Tickets Affected Equipment"
        verbose_name_plural = "Tickets Affected Equipment"

    def __str__(self):
        return f"Ticket {self.ticket.id} affects Equipment {self.equipment.id}"
