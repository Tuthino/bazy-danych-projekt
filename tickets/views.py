from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from users.decorators import *
from .models import Ticket, Comment, TicketType, TicketStatusType, TicketsAffectedEquipment, CommentType,Category, TicketAcknowledgmentStatus, TicketRequestedTeam
from equipments.models import *
from django.utils.dateparse import parse_datetime
import logging
from django.utils import timezone


logger = logging.getLogger('custom') 

@user_loggedin_required

#TODO: If there are no filters applied for dates, then do not include them in the url?
def ticket_list_view(request):
    """View to list all tickets with flexible filtering by start and resolved dates."""
    user = getSessionUser(request)

    # Get filter parameters from the request
    status_id = request.GET.get("status")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    resolved_start_date = request.GET.get("resolved_start_date")
    resolved_end_date = request.GET.get("resolved_end_date")
    filter_type = request.GET.get("filter_type")  # Determines the date filtering logic

    tickets = Ticket.objects.select_related('type', 'creator', 'owner_team', 'status')

    # Filter by status if provided
    if status_id:
        tickets = tickets.filter(status_id=status_id)

    # Apply filtering for issue_started
    if filter_type == "after" and start_date:
        tickets = tickets.filter(issue_started__gte=start_date)
    elif filter_type == "before" and end_date:
        tickets = tickets.filter(issue_started__lte=end_date)
    elif filter_type == "between" and start_date and end_date:
        tickets = tickets.filter(issue_started__gte=start_date, issue_started__lte=end_date)

    # Apply filtering for issue_resolved
    if resolved_start_date:
        tickets = tickets.filter(issue_resolved__gte=resolved_start_date)
    if resolved_end_date:
        tickets = tickets.filter(issue_resolved__lte=resolved_end_date)

    # Get all status types for the filter dropdown
    statuses = TicketStatusType.objects.all()

    return render(request, 'tickets/ticket_list.html', {
        'tickets': tickets,
        'statuses': statuses,
        'selected_status': int(status_id) if status_id else None,
        'start_date': start_date,
        'end_date': end_date,
        'resolved_start_date': resolved_start_date,
        'resolved_end_date': resolved_end_date,
        'filter_type': filter_type,
        'user': user
    })

@user_loggedin_required
def ticket_create_view(request):
    """View to create a new ticket."""
    user = getSessionUser(request)
    if request.method == "POST":
        type_id = request.POST.get("type")
        category_id = request.POST.get("category")
        owner_team_id = request.POST.get("owner_team")
        status_id = request.POST.get("status")
        issue_started = request.POST.get("issue_started")

        logger.info(f"Form Data: {request.POST}")
        if not all([type_id, category_id, owner_team_id, status_id, issue_started]):
            messages.error(request, "All fields are required.")
            return redirect("ticket_create")

        try:
            ticket_type = TicketType.objects.get(id=type_id)
            category = Category.objects.get(id=category_id) 
            owner_team = Team.objects.get(id=owner_team_id)
            ticket_status = TicketStatusType.objects.get(id=status_id)

            Ticket.objects.create(
                type=ticket_type,
                creator=user,
                category=category,
                owner_team=owner_team,
                status=ticket_status,
                issue_started=issue_started,
            )
            logger.info(f"Form Data: {request.POST}")
            logger.info(request, "Ticket created successfully.")
            return redirect("ticket_list")
        except (TicketType.DoesNotExist, Team.DoesNotExist, TicketStatusType.DoesNotExist):
            logger.error(request, "Invalid selection for ticket type, team, or status.")

    ticket_types = TicketType.objects.all()
    status_types = TicketStatusType.objects.all()
    teams = Team.objects.all()
    categories = Category.objects.all()
    return render(request, 'tickets/ticket_create.html', {
        'ticket_types': ticket_types,
        'status_types': status_types,
        'teams': teams,
        'categories':categories,
        'user':user
    })


@user_loggedin_required
def ticket_detail_view(request, ticket_id):
    """View to manage a ticket, add comments, and manage requested team statuses."""
    user = getSessionUser(request)
    ticket = get_object_or_404(Ticket, id=ticket_id)
    comments = ticket.comments.select_related('username', 'comment_type')
    creator_team = ticket.owner_team  
    
    affected_equipments = TicketsAffectedEquipment.objects.select_related("equipment").filter(ticket=ticket)
    available_equipment = Equipment.objects.exclude(
        id__in=affected_equipments.values_list("equipment_id", flat=True)
    )
    if request.method == "POST":
        if "add_comment" in request.POST:
            comment_text = request.POST.get("comment_text")
            comment_type_id = request.POST.get("comment_type")
            if not comment_text or not comment_type_id:
                messages.error(request, "Comment text and type are required.")
                return redirect("ticket_detail", ticket_id=ticket.id)

            try:
                comment_type = CommentType.objects.get(id=comment_type_id)
                Comment.objects.create(
                    ticket=ticket,
                    username=user,
                    comment_text=comment_text,
                    comment_type=comment_type,
                )
                messages.success(request, "Comment added successfully.")
                return redirect("ticket_detail", ticket_id=ticket.id)
            except CommentType.DoesNotExist:
                messages.error(request, "Invalid comment type.")

        elif "request_team" in request.POST:
            # Handle requesting a team
            team_id = request.POST.get("team_id")
            if not team_id:
                messages.error(request, "You must select a team.")
                return redirect("ticket_detail", ticket_id=ticket.id)

            try:
                team = Team.objects.get(id=team_id)
                status = TicketAcknowledgmentStatus.objects.get(name="Pending")  # Default status
                TicketRequestedTeam.objects.create(
                    ticket=ticket,
                    team=team,
                    status=status,
                )
                messages.success(request, f"Team {team.name} requested successfully.")
            except Team.DoesNotExist:
                messages.error(request, "Invalid team.")
            except TicketAcknowledgmentStatus.DoesNotExist:
                messages.error(request, "Default status not found.")

        elif "update_status" in request.POST:
            # Handle updating the requested team status (for requested teams)
            requested_team_id = request.POST.get("requested_team_id")
            new_status_id = request.POST.get("status")
            if not requested_team_id or not new_status_id:
                messages.error(request, "Invalid request. Please try again.")
                return redirect("ticket_detail", ticket_id=ticket.id)

            try:
                requested_team = TicketRequestedTeam.objects.get(id=requested_team_id, ticket=ticket)
                if not requested_team.team.users.filter(user=user).exists():
                    messages.error(request, "You are not authorized to update this team's status.")
                    return redirect("ticket_detail", ticket_id=ticket.id)

                new_status = TicketAcknowledgmentStatus.objects.get(id=new_status_id)
                requested_team.status = new_status
                requested_team.save()

                messages.success(request, f"Status updated for team: {requested_team.team.name}.")
            except TicketRequestedTeam.DoesNotExist:
                messages.error(request, "Requested team entry not found.")
            except TicketAcknowledgmentStatus.DoesNotExist:
                messages.error(request, "Invalid status.")

        elif "resolve_ticket" in request.POST:
            # Handle resolving the ticket (only allowed for owner team members)
            if not creator_team or not creator_team.users.filter(user=user).exists():
                messages.error(request, "You are not authorized to resolve this ticket.")
                return redirect("ticket_detail", ticket_id=ticket.id)

            try:
                resolved_status = TicketStatusType.objects.get(name="Resolved")  # Ensure a "Resolved" status exists
                ticket.status = resolved_status
                ticket.issue_resolved = timezone.now()  # Mark resolved time
                ticket.save()
                messages.success(request, "Ticket resolved successfully.")
            except TicketStatusType.DoesNotExist:
                messages.error(request, "Resolved status not defined.")
            return redirect("ticket_detail", ticket_id=ticket.id)

        elif "update_ticket_status" in request.POST:
            # Allow the owner team to update the ticket's overall status
            if not creator_team or not creator_team.users.filter(user=user).exists():
                messages.error(request, "You are not authorized to update the ticket status.")
                return redirect("ticket_detail", ticket_id=ticket.id)
            new_ticket_status_id = request.POST.get("ticket_status")
            if not new_ticket_status_id:
                messages.error(request, "Please select a valid ticket status.")
                return redirect("ticket_detail", ticket_id=ticket.id)
            try:
                new_ticket_status = TicketStatusType.objects.get(id=new_ticket_status_id)
                ticket.status = new_ticket_status
                ticket.save()
                messages.success(request, "Ticket status updated successfully.")
            except TicketStatusType.DoesNotExist:
                messages.error(request, "Invalid ticket status selected.")
            return redirect("ticket_detail", ticket_id=ticket.id)

        elif "add_affected_equipment" in request.POST:
            # Handle adding affected equipment
            equipment_id = request.POST.get("equipment_id")
            if not equipment_id:
                messages.error(request, "Please select equipment to add.")
                return redirect("ticket_detail", ticket_id=ticket.id)

            try:
                equipment = Equipment.objects.get(id=equipment_id)
                TicketsAffectedEquipment.objects.create(ticket=ticket, equipment=equipment)
                messages.success(request, f"Equipment '{equipment.name}' added to affected list.")
            except Equipment.DoesNotExist:
                messages.error(request, "Invalid equipment selected.")

        elif "remove_affected_equipment" in request.POST:
            # Handle removing affected equipment
            affected_id = request.POST.get("affected_id")
            try:
                affected_equipment = TicketsAffectedEquipment.objects.get(id=affected_id, ticket=ticket)
                affected_equipment.delete()
                messages.success(request, "Affected equipment removed successfully.")
            except TicketsAffectedEquipment.DoesNotExist:
                messages.error(request, "Selected equipment not found in affected list.")

        return redirect("ticket_detail", ticket_id=ticket.id)

    # Query additional data for the template:
    comment_types = CommentType.objects.all()
    available_teams = Team.objects.exclude(id__in=ticket.requested_teams.values_list('team_id', flat=True))
    requested_teams = ticket.requested_teams.select_related('team', 'status')
    acknowledgment_statuses = TicketAcknowledgmentStatus.objects.all()

    # Flag each requested team to indicate if the user is part of that team
    for requested_team in requested_teams:
        requested_team.user_part_of_team = requested_team.team.users.filter(user=user).exists()
    show_actions = any(team.user_part_of_team for team in requested_teams)

    # Determine if the user belongs to the owner team
    can_resolve = creator_team.users.filter(user=user).exists()

    ticket_statuses = TicketStatusType.objects.all()

    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'show_actions': show_actions,
        'comments': comments,
        'can_resolve': can_resolve,
        'comment_types': comment_types,
        'available_teams': available_teams,
        'acknowledgment_statuses': acknowledgment_statuses,
        'requested_teams': requested_teams,
        'ticket_statuses': ticket_statuses,  
        'user': user,
        'affected_equipments': affected_equipments,
        'available_equipment': available_equipment
    })



@user_loggedin_required
def my_team_tickets_view(request):
    """View to list all tickets assigned to teams the user belongs to and transferred tickets."""
    user = getSessionUser(request)

    user_teams = Team.objects.filter(users__user=user)

    status_filter = request.GET.get('status')

    tickets_query = Ticket.objects.filter(owner_team__in=user_teams).select_related('type', 'status', 'owner_team')

 
    requested_tickets_query = TicketRequestedTeam.objects.filter(
        team__in=user_teams
    ).select_related('ticket__type', 'ticket__status', 'team', 'status')

    # Apply status filter if specified
    if status_filter:
        tickets_query = tickets_query.filter(status__id=status_filter)
        requested_tickets_query = requested_tickets_query.filter(ticket__status__id=status_filter)

    statuses = TicketStatusType.objects.all()

    return render(request, 'tickets/my_teams_tickets.html', {
        'tickets': tickets_query,
        'requested_tickets': requested_tickets_query,
        'user_teams': user_teams,
        'statuses': statuses,
        'selected_status': status_filter,
        'user': user,
    })
