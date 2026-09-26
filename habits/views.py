from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Habit, CheckIn, Pup
from django.shortcuts import get_object_or_404
from datetime import date

# Create your views here.

# sign up for pupdate
def signup(request): 
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid(): # checks if passwords match and if the user is available
            user = form.save() # user is in the database
            login(request, user) # log in so they dont have to again
            return redirect('/')
    else: # just visiting the page
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# home page that shows the user's habits and pup (IF THEY ARE LOGGED IN)
@login_required # if you are not logged in, you'll be sent to the login page
def home(request):
    habits = Habit.objects.filter(user=request.user) # shows USER'S habits only
    pup = Pup.objects.filter(user=request.user).first() 
    return render(request, 'habits/home.html', {'habits': habits, 'pup': pup})

# add a new habit for the user logged in
@login_required
def add_habit(request): 
    if request.method == 'POST':
        name = request.POST.get('name')
        if name: # ignores empty submissions
            Habit.objects.create(user=request.user, name=name)
    return redirect('home')

# marking a habit as done
@login_required
def check_in(request, habit_id):
    if request.method == 'POST':
        # finds the habit if it belongs to the user, that way nobody checks off anyone else's habit
        habit = get_object_or_404(Habit, id=habit_id, user=request.user)
        CheckIn.objects.get_or_create(habit=habit, date=date.today())
    return redirect('home')

# deleting a habit
@login_required
def delete_habit(request, habit_id):
    if request.method == 'POST': 
        habit = get_object_or_404(Habit, id=habit_id, user=request.user)
        habit.delete()
    return redirect('home')

# name the user's pup (RENAMABLE)
@login_required
def name_pup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name: #ignoring empty submissions
            Pup.objects.update_or_create(user=request.user, defaults={'name': name}) # updates or creates name if it doesn't exist
    return redirect('home')