from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Habit, CheckIn, Pup, StudyStep
from django.shortcuts import get_object_or_404
from datetime import date, timedelta
from .gemini import make_study_plan

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
    habits = Habit.objects.filter(user=request.user, due_date__isnull=True) # everyday habits ONLY
    # splitting habits into to-do and completed
    tab = request.GET.get('tab', 'todo') # which tab is open?

    done_ids = CheckIn.objects.filter(habit__user=request.user, date=date.today()).values_list('habit_id', flat=True)
    todo_habits = habits.exclude(id__in=done_ids) # not done
    done_habits = habits.filter(id__in=done_ids) # done

    pup = Pup.objects.filter(user=request.user).first() 

    #all checkins for this user's habits
    user_checkins = CheckIn.objects.filter(habit__user=request.user) #habit__user tells it to follow the link from CheckIn to Habit then check its user
    # count unique days with at least one check-in
    # - multiple habits done on the same day will still count as only 1 day
    days_completed = user_checkins.values('date').distinct().count()
    # PUP NEVER SHRINKS
    if days_completed >= 7:
        stage = 'grown'
    elif days_completed >= 3:
        stage = 'young'
    else:
        stage = 'puppy'

    # if its sleepy, there was no check-in today or yesterday
    # date__gte means that the date is greater than or equal to
    yesterday = date.today() - timedelta(days=1)
    checked_in_recently = user_checkins.filter(date__gte=yesterday).exists()
    sleepy = days_completed > 0 and not checked_in_recently # new users cant have a sleepy pup since they just adopted them

    return render(request, 'habits/home.html', {
        'pup': pup,
        'days_completed': days_completed,
        'stage': stage,
        'sleepy': sleepy,
        'tab': tab,
        'todo_habits': todo_habits,
        'done_habits': done_habits,
    })

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
        # syncing it with the plan page
        StudyStep.objects.filter(habit=habit, date=date.today()).update(done=True)
    return redirect('home')

# deleting a habit
@login_required
def delete_habit(request, habit_id):
    if request.method == 'POST': 
        habit = get_object_or_404(Habit, id=habit_id, user=request.user)
        habit.delete()
    return redirect('home')

# undoing a habit from completed and back to to-do
@login_required
def undo_check_in(request, habit_id):
    if request.method == 'POST':
        habit = get_object_or_404(Habit, id=habit_id, user=request.user)
        CheckIn.objects.filter(habit=habit, date=date.today()).delete()
        # syncing it with the plan page
        StudyStep.objects.filter(habit=habit, date=date.today()).update(done=False)
    return redirect('/?tab=done') # do not leave the compeleted tab

# name the user's pup (RENAMABLE)
@login_required
def name_pup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name: #ignoring empty submissions
            Pup.objects.update_or_create(user=request.user, defaults={'name': name}) # updates or creates name if it doesn't exist
    return redirect('home')

@login_required
def plan(request):
    error = None # message showing something went wrong
    open_id = request.GET.get('open') # which dropdown stays open after clicking a check
    form_data = {} # remembers what the user typed so they dont have to retype it again after error

    if request.method == 'POST':
        form_data = request.POST # keep what the user typed
        goal = request.POST.get('goal')
        due = request.POST.get('due_date')
        topics = request.POST.get('topics', '') # this is optional

        if goal and due: # both of these are required
            due_date = date.fromisoformat(due) # turns text into a real date
            if due_date <= date.today():
                error = "Pick a due date in the future!"
            else:
                steps = make_study_plan(goal, due_date, topics) # ask gemini for the plan
                if steps: # gemini gave us a plan
                    # the goal turns into a habit, so if you finish that step, the pup grows
                    habit = Habit.objects.create(user=request.user, name=goal, due_date=due_date)
                    for step_date, task in steps: # save each step
                        StudyStep.objects.create(habit=habit, task=task, date=step_date)
                    return redirect(f"/plan/?open={habit.id}") # open the new plan right away
                else:
                    error = "Couldn't make a plan right now. Try again in a moment!"

    # show all of the user's study steps, and group them by goal
    goals = Habit.objects.filter(user=request.user, due_date__isnull=False).order_by('due_date') # ordering by soonest deadline
    return render(request, 'habits/plan.html', {
        'goals': goals, 
        'error': error, 
        'today': date.today(),
        'form_data': form_data,
        'open_id': open_id,
        })

@login_required
def complete_step(request, step_id):
    if request.method == 'POST':
        # __habit__user only finds steps that belong to the user's goals
        step = get_object_or_404(StudyStep, id=step_id, habit__user=request.user)
        step.done = True # marks it finished
        step.save() # save changes to database
        # count it as a check-in for the day so finishing study steps grows the pup
        CheckIn.objects.get_or_create(habit=step.habit, date=date.today())
        return redirect(f"/plan/?open={step.habit.id}") # keep the goal open
    return redirect('plan')