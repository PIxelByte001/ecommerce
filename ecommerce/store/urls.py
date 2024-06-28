from django.contrib import admin, auth
from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_item/', views.updateItem, name='update_item'),
    path('process_order/', views.processOrder, name="process_order"),

    path('logout/', views._logout, name = 'logout'),
    path('login/', views._login, name = 'login'),
    path('login/action/', views.login_action, name = 'login_action'),
    path('signup/', views.signup, name = 'signup'),
    path('signup/action/', views.signup_action, name = 'signup_action'),
]
