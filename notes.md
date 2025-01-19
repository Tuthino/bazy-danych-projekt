# Users/Authentication (users app):

Handles user registration, login, logout, and profiles.
Models: Username
Views: register_view, login_view, logout_view, profile views.
URLs: /register/, /login/, /logout/, /profile/.

# Teams (teams app):
Manages teams and their memberships.
Models: Team, UsernameTeam.
Views: Team creation, user-team assignment.
URLs: /teams/, /teams/<team_id>/.

# Tickets (tickets app):
Manages ticket creation, updates, and statuses.
Models: AffectedEquipment, TicketStatusType.
Views: Ticket creation, status updates.
URLs: /tickets/, /tickets/<ticket_id>/.

# Dashboard or Main App (dashboard or core app):
Handles the homepage or overall project dashboard.
Could aggregate data from other apps to provide an overview.
URLs: /dashboard/.
