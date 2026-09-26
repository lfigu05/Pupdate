from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Habit
from django.shortcuts import get_object_or_404
from datetime import date
from .models import CheckIn

# Create your views here.

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def home(request):
    habits = Habit.objects.filter(user=request.user)
    return render(request, 'habits/home.html', {'habits': habits})

@login_required
def add_habit(request): 
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Habit.objects.create(user=request.user, name=name)
    return redirect('home')

@login_required
def check_in(request, habit_id):
    if request.method == 'POST':
        habit = get_object_or_404(Habit, id=habit_id, user=request.user)
        CheckIn.objects.get_or_create(habit=habit, date=date.today())
    return redirect('home')