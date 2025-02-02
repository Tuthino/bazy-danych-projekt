from django.urls import path
from . import views

urlpatterns = [
    path('', views.equipment_list_view, name='equipment_list'),
    path('create/', views.equipment_create_view, name='equipment_create'),
    path('detail/<int:equipment_id>/', views.equipment_detail_view, name='equipment_detail'),
    path('edit/<int:equipment_id>/', views.equipment_edit_view, name='equipment_edit'),
]
