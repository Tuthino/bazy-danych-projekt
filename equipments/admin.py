from django.contrib import admin
from .models import (
    EquipmentType,
    Equipment,
)

# admin.site.register(EquipmentType)
# admin.site.register(Equipment)
#
@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'site','type', 'last_change_ticket', 'first_level_support_team', 'second_level_support_team', 'additional_info']

