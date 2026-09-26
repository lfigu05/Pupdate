from django.urls import path
from . import views

urlpatterns = [
    path('accounts/signup/', views.signup, name='signup'),
    path('', views.home, name='home'),
    path('habits/add/', views.add_habit, name='add_habit'),
    path('habits/<int:habit_id>/checkin/', views.check_in, name='check_in'),
    path('pup/name/', views.name_pup, name='name_pup'),
    path('habits/<int:habit_id>/delete/', views.delete_habit, name='delete_habit'),
]