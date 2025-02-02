from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Equipment, EquipmentType, Site
from teams.models import Team, UserTeam
from django.contrib import messages
from users.shared import getSessionUser
from tickets.models import Ticket
from users.decorators import *

def equipment_list_view(request):
    """View to list all equipment."""
    user = getSessionUser(request)
    equipments = Equipment.objects.select_related('type', 'first_level_support_team', 'second_level_support_team')
    # ORM JOINING 2 TABLES
    is_eq_admin = UserTeam.objects.filter(
        user_id=user.id,
        team__equipment_admin=True 
    ).exists()

    return render(request, 'equipments/equipment_list.html', {'equipments': equipments,'is_eq_admin':is_eq_admin, 'user':user})



def equipment_create_view(request):
    """View to create a new equipment."""
    user = getSessionUser(request)
    if request.method == "POST":
        name = request.POST.get("name")
        site_id = request.POST.get("site")
        type_id = request.POST.get("type")
        first_team_id = request.POST.get("first_level_support_team")
        second_team_id = request.POST.get("second_level_support_team")
        additional_info = request.POST.get("additional_info", "")
        last_change_ticket = request.POST.get("last_change_ticket", "").strip()

        # Convert last_change_ticket to integer if provided, otherwise set to None.
        if last_change_ticket == "":
            last_change_ticket = None
        else:
            try:
                last_change_ticket = int(last_change_ticket)
            except ValueError:
                messages.error(request, "Invalid Last Change Ticket value. It must be a number.")
                return redirect(reverse('equipment_create'))

        # Validate that if last_change_ticket is provided, it corresponds to an existing Ticket.
        if last_change_ticket is not None:
            try:
                Ticket.objects.get(id=last_change_ticket)
            except Ticket.DoesNotExist:
                messages.error(request, "Invalid ticket number provided. Ticket does not exist.")
                return redirect(reverse('equipment_create'))

        # Check required fields (last_change_ticket is optional)
        if not all([name, site_id, type_id, first_team_id, second_team_id]):
            messages.error(request, "All fields are required except Additional Info and Last Change Ticket.")
            return redirect(reverse('equipment_create'))

        try:
            site = Site.objects.get(id=site_id)
            type_instance = EquipmentType.objects.get(id=type_id)
            first_team = Team.objects.get(id=first_team_id)
            second_team = Team.objects.get(id=second_team_id)

            Equipment.objects.create(
                name=name,
                site=site,
                type=type_instance,
                first_level_support_team=first_team,
                second_level_support_team=second_team,
                additional_info=additional_info,
                last_change_ticket=last_change_ticket
            )
            messages.success(request, f"Equipment '{name}' created successfully!")
            return redirect(reverse('equipment_list'))
        except (Site.DoesNotExist, EquipmentType.DoesNotExist, Team.DoesNotExist):
            messages.error(request, "Invalid site, type or team selected.")

    equipment_types = EquipmentType.objects.all()
    teams = Team.objects.all()
    sites = Site.objects.all()
    return render(request, 'equipments/equipment_create.html', {
        'equipment_types': equipment_types,
        'sites': sites,
        'teams': teams,
        'user': user
    })


def equipment_edit_view(request, equipment_id):
    """View to edit an equipment."""
    user = getSessionUser(request)
    equipment = get_object_or_404(Equipment, id=equipment_id)

    if request.method == "POST":
        # Retrieve data from the form
        name = request.POST.get("name")
        site_id = request.POST.get("site")
        type_id = request.POST.get("type")
        first_team_id = request.POST.get("first_level_support_team")
        second_team_id = request.POST.get("second_level_support_team")
        additional_info = request.POST.get("additional_info", "")
        last_change_ticket = request.POST.get("last_change_ticket", "").strip()

        if last_change_ticket == "":
            last_change_ticket = None
        else:
            try:
                last_change_ticket = int(last_change_ticket)
            except ValueError:
                messages.error(request, "Invalid Last Change Ticket value. It must be a number.")
                return redirect(reverse('equipment_edit', kwargs={'equipment_id': equipment.id}))

        # Validate that if last_change_ticket is provided, it corresponds to an existing Ticket.
        if last_change_ticket is not None:
            try:
                Ticket.objects.get(id=last_change_ticket)
            except Ticket.DoesNotExist:
                messages.error(request, "Invalid ticket number provided. Ticket does not exist.")
                return redirect(reverse('equipment_edit', kwargs={'equipment_id': equipment.id}))

        try:
            # Fetch related objects
            site_obj = Site.objects.get(id=site_id)
            type_instance = EquipmentType.objects.get(id=type_id)
            first_team = Team.objects.get(id=first_team_id)
            second_team = Team.objects.get(id=second_team_id)

            # Update equipment fields
            equipment.name = name
            equipment.site = site_obj
            equipment.type = type_instance
            equipment.first_level_support_team = first_team
            equipment.second_level_support_team = second_team
            equipment.additional_info = additional_info
            equipment.last_change_ticket = last_change_ticket
            equipment.save()

            messages.success(request, f"Equipment '{equipment.name}' updated successfully!")
            return redirect('equipment_list')
        except (Site.DoesNotExist, EquipmentType.DoesNotExist, Team.DoesNotExist):
            messages.error(request, "Invalid site, type or team selected.")

    equipment_types = EquipmentType.objects.all()
    teams = Team.objects.all()
    sites = Site.objects.all()
    return render(request, 'equipments/equipment_edit.html', {
        'equipment': equipment,
        'equipment_types': equipment_types,
        'teams': teams,
        'sites': sites,
        'user': user
    })


@user_loggedin_required
def equipment_detail_view(request, equipment_id):
    """View to display the details of an equipment and list unresolved tickets affecting it.
       All logged-in users can access this view.
    """
    user = getSessionUser(request)
    equipment = get_object_or_404(Equipment, id=equipment_id)

    # Fetch only unresolved tickets that affect this equipment
    unresolved_tickets = Ticket.objects.filter(
        ticketsaffectedequipment__equipment=equipment
    ).exclude(status__name="Resolved")  

    return render(request, 'equipments/equipment_details.html', {
        'equipment': equipment,
        'tickets': unresolved_tickets,  
        'user': user,
    })
