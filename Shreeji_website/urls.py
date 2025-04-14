"""
URL configuration for Shreeji_website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from shreejiapp import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('',views.homepage,name='homepage'),
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('product_page/',views.userside_productPage,name='userside_productPage'),
    path('admin/',include('custom_admin.urls')),
    path('staff/',include('staff.urls')),
    path('logout/',views.user_logout_view,name='user_logout'),
    path('userside_orderPage/',views.userside_orderPage,name='userside_orderPage'),
    path('user_orders/',views.user_orders,name='user_orders'),
    path('cart/',views.cart_page,name='cart'),
    path('add_to_cart/',views.add_to_cart,name='add_to_cart'),
    path('remove_from_cart/',views.remove_from_cart,name='remove_from_cart'),
    path('checkout_page/',views.checkout,name='checkout'),
    path('process_order/',views.process_order,name='process_order'),
    path('contact_us/',views.contact_us,name='contact_us'),
    path('aboutUs/',views.aboutUs,name='aboutUs'),
    path('user_messages/',views.user_messages, name='user_messages'),
    path('search/', views.search_products, name='search_products'),
    path('download-invoice/<int:order_id>/',views.generate_invoice, name='download_invoice'),
    path('profile_view/', views.profile_view, name='profile_view'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)