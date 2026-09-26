from django.contrib import admin
from .models import Habit, CheckIn, Pup

# Register your models here.
admin.site.register(Habit)
admin.site.register(CheckIn)
admin.site.register(Pup)