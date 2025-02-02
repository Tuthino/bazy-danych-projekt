from django.contrib import admin
from .models import Ticket, TicketType, TicketsAffectedEquipment, TicketStatusType, Comment, CommentType,Category,TicketAcknowledgmentStatus,TicketRequestedTeam

#TODO: Register those views to show important fields, not only the name ;p 
admin.site.register(Ticket)
admin.site.register(TicketType)
admin.site.register(TicketStatusType)
admin.site.register(Comment)
admin.site.register(CommentType)
admin.site.register(Category)
admin.site.register(TicketAcknowledgmentStatus)
admin.site.register(TicketRequestedTeam)
admin.site.register(TicketsAffectedEquipment)
