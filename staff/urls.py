from django.urls import path
from . import views

urlpatterns = [
    path('staff_login/', views.staff_login, name='staff_login'),
    path('', views.staff_dashboard, name='staff_dashboard'),
    path('staff_orders/', views.staff_order_management, name='order_management'),
    path('staff_deliveries/', views.staff_delivery_management, name='delivery_management'),
    path('staff_inventory/', views.staff_inventory_management, name='inventory_management'),
    path('staff_activity/', views.activity_log, name='activity_log'),
    path('staff_profile/', views.staff_profile, name='staff_profile'),
    path('staff_logout/', views.staff_logout, name='staff_logout'),
   
]









