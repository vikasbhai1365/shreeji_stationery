from django.urls import path
from . import views

urlpatterns = [
    # path('', views.admin_login, name='admin_login'),
    path('',views.custom_admin_view,name='admin_dashboard'),
    path('users/', views.user_page, name='user_page'),
    path('delete_users/', views.delete_users, name='delete_users'),
    path('add_product/', views.add_product, name='add_product'),
    path('product_list/',views.product_list,name='product_list'),
    path('product/',views.product_page,name='product_page'),
    path('category_page/',views.category_page,name='category_page'),
    path('brand_page/',views.brand_page,name='brand_page'),
    path('color_page/',views.color_page,name='color_page'),
    path('add_category/',views.add_category,name='add_category'),
    path('add_brand/',views.add_brand,name='add_brand'),
    path('add_color/',views.add_color,name='add_color'),
    path('show_category/',views.show_category,name='show_category'),
    path('show_brand/',views.show_brand,name='show_brand'),
    path('show_color/',views.show_color,name='show_color'),
    path('admin_logout/',views.admin_logout_view,name='admin_logout_view'),
    path('admin_login/',views.admin_login,name='admin_login'),
    path('update_or_delete_product/<int:product_id>/',views.update_or_delete_product,name='update_or_delete_product'),
    path('update_category/<int:category_id>/',views.update_categoryPage,name='update_categoryPage'),

    path('update_product/<int:product_id>/',views.update_productPage,name='update_productPage'),
    path('admin_orders/',views.admin_orders, name='admin_orders'),
    path('update_order_status/<int:order_id>/',views.update_order_status, name='update_order_status'),
    path('admin_base/',views.admin_base,name='admin_base'),

    path('admin_orders/', views.admin_orders, name='admin_orders'),
    path('update_status/', views.update_status, name='update_status'),
    path('delete_order/', views.delete_order, name='delete_order'),


    path("admin_contact_messages/",views.admin_contact_messages, name="admin_contact_messages"),
    path("admin_reply_message/<int:message_id>/", views.reply_message, name="reply_message"),

    path('delete_product/<int:color_id>/',views.delete_color,name='delete_color'),
    path('delete_brand/<int:brand_id>/',views.delete_brand,name='delete_brand'),
    path('delete_category/<int:category_id>/',views.update_or_delete_category,name='update_or_delete_category'),
    
    path('manage-delivery/', views.manage_deliveries_view, name='manage_delivery'),
    path('reports/', views.reports_view, name='reports'),
    path('update-delete-color/<int:color_id>/',views.update_or_delete_color,name='update_or_delete_color'),
    path('update_color/<int:color_id>/',views.update_colorPage,name='update_colorPage'),
    path('update-delete-brand/<int:brand_id>/',views.update_or_delete_brand,name='update_or_delete_brand'),
    path('update_brand/<int:brand_id>/',views.update_brandPage,name='update_brandPage'),

   
]









