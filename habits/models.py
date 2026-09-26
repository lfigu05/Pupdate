from django.db import models # model tools
from django.contrib.auth.models import User # built-in user table

# Create your models here.

# class start
class Habit(models.Model): # naming my table
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100) # a name can have max 100 characters
    created_at = models.DateTimeField(auto_now_add=True) # saving date and time when the habit is made

    def __str__(self):
        return self.name

class CheckIn(models.Model): # naming my table
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE) # each check belongs to 1 habit, 1 habit can have many check-ins
    date = models.DateField() # stores the day it was done

    def __str__(self): # added this because on the admin panel, the objects would return with (1), (2),...
        return f"{self.habit.name} on {self.date}"

class Pup(models.Model): # naming my table
    user = models.OneToOneField(User, on_delete=models.CASCADE) # each user has exactly 1 pup, and each pup has exactly one user
    name = models.CharField(max_length=100) # a name can have max 100 characters

    def __str__(self):
        return self.name
