from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse
from .forms import *
from .models import *
from .utils import *
from django.http import JsonResponse
import json
from django.core.serializers.json import DjangoJSONEncoder
import datetime, random


# Create your views here.

def Home(request):
    return render(request, "index.html")



def login_view(request):
    if request.method == 'POST':
        if('signup' in request.POST):
            username = request.POST['username']
            name = request.POST['name']
            password = request.POST['password']
            password_confirm = request.POST.get('password_confirm')

            # Check if both passwords match
            context = {
                'username': username,  # Always return the username
                'name': name,  # Always return the name
                'state':True
            }

            # Check if both passwords match
            if password != password_confirm:
                context['error_sub'] = 'Passwords do not match.'
                context['reset_password'] = True  # Signal to reset only the password fields
                return render(request, 'index1.html', context)

            if User.objects.filter(username=username).exists():
                context['error_sub'] = 'Username already in use.'
                context['reset_username'] = True  # Signal to reset the username and password
                context['username'] = ''
                return render(request, 'index1.html', context)

            user = User.objects.create_user(username=username, password=password)
            user.first_name= name
            user.save()
            UserSettings.objects.create(user=user)
            UserProfile.objects.create(user=user)
            # Log the user in (optional)

            login(request, user)
            return redirect('home')
        
        elif('login' in request.POST):

            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to home page or dashboard
            else:
                # Return an 'invalid login' error messages

                return render(request, 'index1.html', {'error_log': 'Invalid login credentials.'})
    return render(request, 'index1.html')


@login_required
def home_view(request):
    opening_lines = [("Hey there, superstar!", "Ready to conquer today?"),
                     ("Hey, " + request.user.first_name + "!", "What's cookin', good lookin'?"),
                     ("Oh, it’s you, " + request.user.first_name + "!", "Let’s get those gears moving!"),
                     ("What's new, " + request.user.first_name + "?", "Ready to push your limits?"),
                     ("Whatup, " + request.user.first_name + "!", "Let's make today unforgettable."),
                     ("Yo, " + request.user.first_name + "!", "Ready to smash some goals?"),
                     ("Yo, Homie!", "What's the vibe today?"),
                     ("Howdy, partner!", "Ready for some action?"),
                     ("What's cookin', good lookin'?", "Got some big plans today?"),
                     ("Hey, hey!", "What’s on your agenda today?"),
                     ("What's poppin', champion?", "Ready to break some records?"),
                     ("Hello, trailblazer!", "What adventure awaits us?"),
                     ("What’s up, buttercup?", "Time to jump and amp up!"),
                     ("What's brewin', " + request.user.first_name + "?", "Time to stir up some muscle stew!"),
                     ("Yooo-hooo, " + request.user.first_name + "!", "Ready to whoop it up at the workout?"),
                     ("My homie!", "All good under the hood?"),                     
                     ("Ahoy there, " + request.user.first_name + "!", "Ready to navigate the fitness seas?"),
                     ("What’s up, rockstar?", "Ready to roll?"),
                     ("Greetings, "+ request.user.first_name + "!", "Ready to power through another day?")]
    random_line = random.choice(opening_lines)
    today = timezone.now().date()

    # Query for upcoming sessions
    upcoming_sessions = Session.objects.filter(date__gte=today, user=request.user).order_by('date')[:3]
    last_session = Session.objects.filter(date__lt=timezone.now().date(), user=request.user).order_by('-date').first()
    last_prs = PersonalRecord.objects.filter(user=request.user).order_by('-date')[:5]


    last_session_lst=[]
    if last_session:
        exercises = last_session.session_exercises.all()
        for exercise in exercises:

            exercise.set_info = exercise.set_list.all()

        last_session_lst.append((last_session, exercises))

    context = {
        'upcoming_sessions': upcoming_sessions,
        'last_session': last_session_lst,
        'last_prs': last_prs,
        'opening': random_line
    }
    return render(request, 'home.html', context)

@login_required
def create_workout_view(request):
    form = ExerciseForm()
    exercise_lst = ExerciseList.objects.all().order_by('name')
    custom_exercise_lst = CustomExerciseList.objects.all()
    exercise_tuple=[]
    for i in range(len(exercise_lst)):
        exercise_tuple.append((i,exercise_lst[i]))

    # Your home page logic here
    return render(request, 'create_workout.html',{'form': form,  'exercise_lst': exercise_lst, "custom_exercise_lst": custom_exercise_lst})

@login_required
def my_workout_view(request):
    workouts = WorkoutName.objects.filter(user=request.user).order_by('-id')
    context= []
    for workout in workouts:
        exercises = workout.exercise_set.all()
        context.append((workout,exercises))


    return render(request, 'my_workout.html',{'workouts': workouts, 'context': context})

def add_custom_exercise(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:

            user = request.user
            custom_exercise = CustomExerciseList.objects.create(
                user=user,
                name=name
            )
            return JsonResponse({"success": True, "message": "Custom exercise added successfully.",'name': custom_exercise.name, 'id': custom_exercise.id})
        else:
            return JsonResponse({"success": False, "error": "Form data is not valid."})



@login_required
def edit_workout(request, workout_id=None):
    workout = None
    if workout_id:
        workout = get_object_or_404(WorkoutName, id=workout_id, user=request.user)

    if request.method == "POST":
        workout_name = request.POST.get('workoutName')
        if workout:
            workout.name = workout_name
        else:
            workout = WorkoutName(user=request.user, name=workout_name)
        workout.save()


        if workout_id:
            workout.exercise_set.all().delete()

        exercises = request.POST.getlist('exercises[]')
        reps_list = request.POST.getlist('reps[]')
        sets_list = request.POST.getlist('sets[]')

        for exercise, reps, sets in zip(exercises, reps_list, sets_list):
            Exercise.objects.create(workout=workout, exercise=exercise, reps=reps, sets=sets)

        return redirect('my_workout')

    else:
        all_exercises = ExerciseList.objects.all().order_by('name')
        all_custom_exercises = CustomExerciseList.objects.all()
        #all_exercises = ['Push-up', 'Pull-up', 'Squat', 'Lunge']
        exercises = workout.exercise_set.all() if workout else None

        return render(request, 'edit_workout.html', {'workout': workout, 'exercises': exercises, 'all_exercises':all_exercises,'all_custom_exercises':all_custom_exercises})



@login_required
def submit(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = request.POST
        workout_id = data.get('workoutId')
        exercises = data.getlist('exercises[]')
        reps = data.getlist('reps[]')
        sets = data.getlist('sets[]')
        name = data.get('workoutName')

        if name:
            if workout_id:
                workout = get_object_or_404(WorkoutName, id=workout_id, user=request.user)
                workout.delete()
            workout = WorkoutName.objects.create(name=name, user=request.user)

            for exercise, reps, sets in zip(exercises, reps, sets):
                if exercise:  # Assuming you've validated that the exercise field isn't empty
                    Exercise.objects.create(
                        name=workout,
                        exercise=exercise,
                        reps=reps,
                        sets=sets
                    )
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "Please provide a workout name."})
    return JsonResponse({"success": False, "error": "Invalid request"})

def delete_workout(request, workout_id):
    if request.method == 'POST':
        workout = get_object_or_404(WorkoutName, id=workout_id)
        today = datetime.date.today()
    # Get all sessions associated with the workout that are in the future
        future_sessions = Session.objects.filter(workout=workout_id, date__gt=today)
        # Set workout to None for future sessions
        for session in future_sessions:
            session.workout = None
            session.save()
        workout.delete()

        return JsonResponse({'status': 'success', 'message': 'Session deleted successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



@login_required
def my_sessions1(request):
    sessions = Session.objects.filter(user=request.user).order_by('date').reverse()
    
    session_lst =[]

    for session in sessions:
        exercises = session.session_exercises.all()
        for exercise in exercises:

            exercise.set_info = exercise.set_list.all()

        session_lst.append((session, exercises))

    return render(request, 'my_session.html', {'sessions': session_lst})

@login_required
def my_sessions(request):
    session_lst =[]
    today = datetime.date.today()
    current_year = today.year
    current_month = today.month
    sessions = Session.objects.filter(user=request.user)

    if request.method == 'POST':

        form = MonthFilterForm(request.POST)
        if form.is_valid():
            year = form.cleaned_data.get('year')
            month = form.cleaned_data.get('month')
            current_year = int(year)
            current_month= int(month)

        start_date = datetime.date(int(year), int(month), 1)
        end_date = datetime.date(int(year), int(month) + 1, 1) if int(month) < 12 else datetime.date(year + 1, 1, 1)
        sessions = sessions.filter(date__range=[start_date, end_date - datetime.timedelta(days=1)]).order_by('date').reverse()
        for session in sessions:
            exercises = session.session_exercises.all()
            for exercise in exercises:

                exercise.set_info = exercise.set_list.all()

            session_lst.append((session, exercises))
        html = render_to_string('partials/session_accordion.html', {'sessions': session_lst}, request)
        return JsonResponse({'html': html})
    
    form = MonthFilterForm()
    year=current_year
    month=current_month

    start_date = datetime.date(int(year), int(month), 1)
    end_date = datetime.date(int(year), int(month) + 1, 1) if int(month) < 12 else datetime.date(year + 1, 1, 1)
    sessions = sessions.filter(date__range=[start_date, end_date - datetime.timedelta(days=1)]).order_by('date').reverse()


    for session in sessions:
        exercises = session.session_exercises.all()
        for exercise in exercises:

            exercise.set_info = exercise.set_list.all()

        session_lst.append((session, exercises))

    context = {
        'sessions': session_lst, 
        'form': form, 
        'years': form.fields['year'].choices, 
        'months': form.fields['month'].choices, 
        'current_year':current_year, 
        'current_month': current_month

    }
    return render(request, 'my_session.html', context)





@login_required
def create_session(request):

    if request.method == 'POST':
        data = request.POST


        form = SessionForm(request.POST, user=request.user)


        if form.is_valid():

            new_session = form.save(commit=False)
            new_session.user = request.user
            new_session.save()
            # Redirect to a page where the user can add details like weights for each exercise
            return redirect('add_details', session_id=new_session.id)
    else:
        form = SessionForm(user=request.user)
    return render(request, 'create_session.html', {'form': form})

@login_required
def add_details(request, session_id):
    session = get_object_or_404(Session, id=session_id, user=request.user)

    exercises = session.workout.exercise_set.all()  # Adjust based on your related_name or model structure

    for exercise in exercises:

        exercise.range_sets = range(1, exercise.sets+1)


    if request.method == 'POST':
        for exercise in exercises:
            session_exercise = SessionExercise.objects.create(
                session=session,
                exercise=exercise.exercise,
                reps = exercise.reps,
                sets= exercise.sets,
            )

            weight_lst = request.POST.getlist(f'weight_{exercise.id}[]') #use getlist to get all elements with same name!!
            partials_lst = request.POST.getlist(f'partials_{exercise.id}[]')
            reps_lst = request.POST.getlist(f'reps_{exercise.id}[]')
            index = 1
            for weight, reps, partials in zip(weight_lst, reps_lst, partials_lst):
                new_set = SessionExerciseSet.objects.create(
                    session_exercise= session_exercise,
                    set = index,
                    weight = weight if weight else 0,
                    reps = reps if reps else 0,
                    partials = partials if partials else 0,

                )
                check_and_update_pr(session.user, session_exercise.exercise, new_set.reps, float(new_set.weight), session)
                calculate_progression_index(session.user, session_exercise.exercise, session)
                index+=1

        # Process submitted exercise details here
        # You might manually process each field in the POST data or use formsets
        session.rating = request.POST.get('rating') if request.POST.get('rating') else None
        session.save()
        return redirect('my_session')  # or wherever you want to redirect to after saving

    return render(request, 'add_details.html', {'session': session, 'exercises': exercises})

@login_required
def edit_session(request, session_id=None):
    session = None
    if session_id:
        session = get_object_or_404(Session, id=session_id, user=request.user)
        exercises = session.session_exercises.all()  # Adjust based on your related_name or model structure

        for exercise in exercises:
            exercise.range_sets = range(1, len(exercise.set_list.all())+1)

    if request.method == "POST":
        all_prs =  PersonalRecord.objects.filter(session = session)
        all_prog =Progression.objects.filter(session = session)
        all_prs.delete()
        all_prog.delete()

        for exercise in exercises:
            weight_lst = request.POST.getlist(f'weight_{exercise.id}[]') #use getlist to get all elements with same name!!
            partials_lst = request.POST.getlist(f'partials_{exercise.id}[]')
            reps_lst = request.POST.getlist(f'reps_{exercise.id}[]')
            sets = exercise.set_list.all()

            for i in range(len(weight_lst)):
                # Check if a set exists for this index
                if i < len(sets):
                    set = sets[i]
                    weight = weight_lst[i] if weight_lst[i] else 0
                    reps = reps_lst[i] if reps_lst[i] else 0
                    partials = partials_lst[i] if partials_lst[i] else 0
                    
                    # Update the set instance
                    set.weight = weight
                    set.reps = reps
                    set.partials = partials
                    set.save(update_fields=['weight', 'partials', 'reps'])
                    check_and_update_pr(session.user, exercise.exercise, set.reps, float(set.weight), session)
                    calculate_progression_index(session.user, exercise.exercise, session)
                else:
                    new_set = SessionExerciseSet.objects.create(
                        session_exercise= exercise,
                        set = i+1,
                        weight = weight_lst[i] if weight_lst[i] else 0,
                        reps = reps_lst[i] if reps_lst[i] else 0,
                        partials = partials_lst[i] if partials_lst[i] else 0
                    )
                    check_and_update_pr(session.user, exercise.exercise, new_set.reps, float(new_set.weight), session)
                    calculate_progression_index(session.user, exercise.exercise, session)

        session.rating = request.POST.get('rating') if request.POST.get('rating') else None
        session.save()
        return redirect('my_session')

    else:
        all_exercises = ExerciseList.objects.all()
        #sall_exercises = ['Push-up', 'Pull-up', 'Squat', 'Lunge']
        exercises = session.session_exercises.all() if session else None

        for exercise in exercises:
            sets = exercise.set_list.all()
            exercise.set_data = sets
        return render(request, 'edit_session.html', {'session': session, 'exercises': exercises, 'all_exercises':all_exercises})


def delete_session(request, session_id):
    if request.method == 'POST':
        session = get_object_or_404(Session, id=session_id)
        session.delete()
        return JsonResponse({'status': 'success', 'message': 'Session deleted successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def list_friends(request):
    user_id = request.user.id
    all_users = User.objects.exclude(id=user_id)  # Exclude the current user

    # Retrieve all friendships involving the current user
    friendships = Friendship.objects.filter(creator_id=user_id) | Friendship.objects.filter(friend_id=user_id)
    
    # Determine friend IDs based on friendships
    friend_ids = {friendship.friend_id if friendship.creator_id == user_id else friendship.creator_id for friendship in friendships}
    friends = User.objects.filter(id__in=friend_ids).order_by('first_name')

    # Non-friends are all users minus friends
    non_friends = all_users.exclude(id__in=friend_ids).order_by('first_name')

    # Retrieve all active friend requests sent by and to the user
    friend_requests_received = FriendRequest.objects.filter(receiver_id=user_id, is_active=True)
    friend_requests_sent = FriendRequest.objects.filter(sender_id=user_id, receiver_id__in=non_friends.values_list('id', flat=True), is_active=True)

    received_friend_request_ids = FriendRequest.objects.filter(receiver=request.user, is_active=True).values_list('sender_id', flat=True)
    non_friends = all_users.exclude(id__in=list(friend_ids) + list(received_friend_request_ids)).order_by('first_name')
    context = {
        'friends': friends,
        'non_friends': non_friends,
        'requests_received': friend_requests_received,
        'requests_sent': {req.receiver_id for req in friend_requests_sent},
    }
    return render(request, 'list_friends.html', context)


def send_friend_request(request, user_id):
    from_user = request.user
    to_user = get_object_or_404(User, id=user_id)

    if from_user != to_user:

        friend_request, created = FriendRequest.objects.get_or_create(sender=from_user, receiver=to_user)
        # Optional: Notify the user or do something if already created
    return redirect('list_friends')  # Adjust this to your needs

@login_required
def add_friend(request, user_id):
    if request.method == "POST":
        friend = get_object_or_404(User, id=user_id)
        # Avoid duplicate friendships
        if not Friendship.objects.filter(creator=request.user, friend=friend).exists():
            Friendship.objects.create(creator=request.user, friend=friend)
        return HttpResponseRedirect(reverse('list_friends'))

def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user, is_active=True)
    Friendship.objects.create(creator=friend_request.sender, friend=friend_request.receiver)
    friend_request.is_active = False
    friend_request.delete()
    return redirect('list_friends')  # Or wherever you list friendships

def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user, is_active=True)
    friend_request.is_active = False
    friend_request.delete()
    return redirect('list_friends')  # Adjust based on where you want to redirect


@login_required
def view_friend_workout(request, user_id):
    user = get_object_or_404(User, id=user_id)
    settings = UserSettings.objects.get(user=user)
    body_metrics = BodyMetric.objects.filter(user=user).order_by('-date').reverse() 
    muscle, fat, weight, bmi= get_metrics_list(body_metrics) 
    last_muscle = muscle[-1][0] if muscle else None
    last_fat = fat[-1][0] if fat else None
    last_weight = weight[-1][0] if weight else None
    last_bmi = bmi[-1][0] if bmi else None

    session_lst =[]
    today = datetime.date.today()
    current_year = today.year
    current_month = today.month
    sessions = Session.objects.filter(user=user)

    all_exercises = ExerciseList.objects.all()
    all_custom_exercises = CustomExerciseList.objects.all()
    exercises_with_progression = Progression.objects.filter(user=user).values_list('exercise', flat=True).distinct()
    exercises_with_prs = PersonalRecord.objects.filter(user=user).values_list('exercise', flat=True).distinct()

    # Check if the current user is friends with the user whose workouts they want to view
    if Friendship.objects.filter(creator=request.user, friend=user).exists() or Friendship.objects.filter(creator=user, friend=request.user).exists():
        workouts = WorkoutName.objects.filter(user=user).order_by('-id')  # Assuming your Workout model has a 'user' field
        workout_exercises= []
        for workout in workouts:
            exercises = workout.exercise_set.all()
            workout_exercises.append((workout,exercises))


        if request.method == 'POST':

            form = MonthFilterForm(request.POST)
            if form.is_valid():
                year = form.cleaned_data.get('year')
                month = form.cleaned_data.get('month')
                current_year = int(year)
                current_month= int(month)

            start_date = datetime.date(int(year), int(month), 1)
            end_date = datetime.date(int(year), int(month) + 1, 1) if int(month) < 12 else datetime.date(year + 1, 1, 1)
            sessions = sessions.filter(date__range=[start_date, end_date - datetime.timedelta(days=1)]).order_by('date').reverse()
            for session in sessions:
                exercises = session.session_exercises.all()
                for exercise in exercises:

                    exercise.set_info = exercise.set_list.all()

                session_lst.append((session, exercises))
            html = render_to_string('partials/session_accordion.html', {'sessions': session_lst}, request)
            return JsonResponse({'html': html})
        
        form = MonthFilterForm()
        year=current_year
        month=current_month
    
        start_date = datetime.date(int(year), int(month), 1)
        end_date = datetime.date(int(year), int(month) + 1, 1) if int(month) < 12 else datetime.date(year + 1, 1, 1)
        sessions = sessions.filter(date__range=[start_date, end_date - datetime.timedelta(days=1)]).order_by('date').reverse()


        for session in sessions:
            exercises = session.session_exercises.all()
            for exercise in exercises:

                exercise.set_info = exercise.set_list.all()

            session_lst.append((session, exercises))

        workout_stats = get_workout_stats_by_timeframe(user)
        stats = False
        for key, value in workout_stats.items():
            if value:
                stats = True

        context = {
            'workouts': workouts, 
            'context': workout_exercises,
            'sessions': session_lst, 
            'form': form, 
            'years': form.fields['year'].choices, 
            'months': form.fields['month'].choices, 
            'current_year':current_year, 
            'current_month': current_month,
            'friend': user, 
            'exercises': exercises_with_progression, 
            'exercises1': exercises_with_prs, 
            'all_exercises':all_exercises, 
            'all_custom_exercises': all_custom_exercises,
            'workout_stats': workout_stats,
            'stats_available': stats,
            'settings': settings,
            'last_muscle': last_muscle,
            'last_fat': last_fat,
            'last_weight': last_weight,
            'last_bmi': last_bmi
        }


        return render(request, 'friend_workout.html', context)
    else:
        # If they're not friends, don't show the workouts
        return render(request, 'error.html', {'message': 'You are not friends with this user.'})
 

login_required
def exercise_progression_view(request):
    all_exercises = ExerciseList.objects.all()
    all_custom_exercises = CustomExerciseList.objects.all()
    exercises_with_progression = Progression.objects.filter(user=request.user).values_list('exercise', flat=True).distinct()
    exercises_with_prs = PersonalRecord.objects.filter(user=request.user).values_list('exercise', flat=True).distinct()

    return render(request, 'exercise_progression.html', {'exercises': exercises_with_progression, 'exercises1': exercises_with_prs, 'all_exercises':all_exercises, 'all_custom_exercises': all_custom_exercises})

def plot_progression(request):
    if request.method == 'POST':
        exercise = request.POST.get('exercise')
        progression = request.POST.get('progression')
        progression_data = Progression.objects.filter(user=request.user, exercise=exercise).order_by('date')

        if(progression == 'Progression Index'):

            progression_plot_data = {
            'dates': [p.date.strftime("%d-%m-%y") for p in progression_data],
            'progression_indexes': [p.progression_index for p in progression_data],
            }
        else:
            progression_plot_data = {
            'dates': [p.date.strftime("%d-%m-%y") for p in progression_data],
            'progression_indexes': [p.progression_over_time for p in progression_data],
            }
        # Serialize progression_plot_data for safe passage into the template
        serialized_progression_plot_data = json.dumps(progression_plot_data, cls=DjangoJSONEncoder)

        context = {
            'progression_plot_data': serialized_progression_plot_data,
        }
        return JsonResponse({"success": True, 'context': context})
    else:
        return JsonResponse({"success": False, "error": "Please provide a workout name."})
    
def plot_progression_friend(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        exercise = request.POST.get('exercise')
        progression = request.POST.get('progression')
        progression_data_friend = Progression.objects.filter(user=user, exercise=exercise).order_by('date')
        include_my_progression = request.POST.get('my_progression')

        if(progression == 'Progression Index'):
            progression_plot_data_friend = {
                'dates': [p.date.strftime("%d-%m-%y") for p in progression_data_friend],
                'friend_progression_indexes': [p.progression_index for p in progression_data_friend],
            }

            progression_plot_data = {}
            if include_my_progression == 'on':
                progression_data = Progression.objects.filter(user=request.user, exercise=exercise).order_by('date')
                dates_combined = sorted(set(progression_plot_data_friend['dates'] + [p.date.strftime("%d-%m-%y") for p in progression_data]))
                progression_my = {p.date.strftime("%d-%m-%y"): p.progression_index for p in progression_data}
                
                progression_plot_data = {
                    'dates': dates_combined,
                    'friend_progression_indexes': [progression_plot_data_friend['friend_progression_indexes'][progression_plot_data_friend['dates'].index(date)] if date in progression_plot_data_friend['dates'] else None for date in dates_combined],
                    'my_progression_indexes': [progression_my[date] if date in progression_my else None for date in dates_combined],
                }
            else:
                progression_plot_data = progression_plot_data_friend

        else:
            progression_plot_data_friend = {
                'dates': [p.date.strftime("%d-%m-%y") for p in progression_data_friend],
                'friend_progression_indexes': [p.progression_over_time for p in progression_data_friend],
            }

            progression_plot_data = {}
            if include_my_progression == 'on':
                progression_data = Progression.objects.filter(user=request.user, exercise=exercise).order_by('date')
                dates_combined = sorted(set(progression_plot_data_friend['dates'] + [p.date.strftime("%d-%m-%y") for p in progression_data]))
                progression_my = {p.date.strftime("%d-%m-%y"): p.progression_over_time for p in progression_data}
                
                progression_plot_data = {
                    'dates': dates_combined,
                    'friend_progression_indexes': [progression_plot_data_friend['friend_progression_indexes'][progression_plot_data_friend['dates'].index(date)] if date in progression_plot_data_friend['dates'] else None for date in dates_combined],
                    'my_progression_indexes': [progression_my[date] if date in progression_my else None for date in dates_combined],
                }
            else:
                progression_plot_data = progression_plot_data_friend

        # Serialize progression_plot_data for safe passage into the template
        serialized_progression_plot_data = json.dumps(progression_plot_data, cls=DjangoJSONEncoder)

        context = {
            'progression_plot_data': serialized_progression_plot_data,
        }
        return JsonResponse({"success": True, 'context': context})
    else:
        return JsonResponse({"success": False, "error": "Please provide a workout name."})
    
def show_reps(request):
    if request.method == 'POST':
        exercise = request.POST.get('exercise')
        if exercise:
            reps = PersonalRecord.objects.filter(exercise=exercise, user=request.user).values_list('reps', flat=True).distinct()
            reps_list = list(reps)
            return JsonResponse({'reps': reps_list})
        else:
            return JsonResponse({'reps': []})
        
def show_reps_friend(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        exercise = request.POST.get('exercise')
        if exercise:
            reps = PersonalRecord.objects.filter(exercise=exercise, user=user).values_list('reps', flat=True).distinct()
            reps_list = list(reps)
            return JsonResponse({'reps': reps_list})
        else:
            return JsonResponse({'reps': []})

def plot_prs(request):
    if request.method == 'POST':
        exercise = request.POST.get('exercise')
        reps = request.POST.get('reps')
        pr_data = PersonalRecord.objects.filter(user=request.user, exercise=exercise, reps=reps).order_by('date')

        pr_plot_data = {
        'dates': [p.date.strftime("%d-%m-%y") for p in pr_data],
        'weight': [p.weight for p in pr_data],
        }

        # Serialize progression_plot_data for safe passage into the template
        serialized_pr_plot_data = json.dumps(pr_plot_data, cls=DjangoJSONEncoder)
        context = {
            'pr_plot_data': serialized_pr_plot_data,
        }
        return JsonResponse({"success": True, 'context': context})
    else:
        return JsonResponse({"success": False, "error": "Please provide a workout name."})

@login_required
def plot_prs_friend(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        exercise = request.POST.get('exercise')
        reps = request.POST.get('reps')
        pr_data_friend = PersonalRecord.objects.filter(user=user, exercise=exercise, reps=reps).order_by('date')

        include_my_prs = request.POST.get('my_prs')
        pr_plot_data_friend = {
            'dates': [p.date.strftime("%d-%m-%y") for p in pr_data_friend],
            'friend_weight': [p.weight for p in pr_data_friend],
        }

        pr_plot_data = {}
        if include_my_prs == 'on':
            pr_data = PersonalRecord.objects.filter(user=request.user, exercise=exercise, reps=reps).order_by('date')
            dates_combined = sorted(set(pr_plot_data_friend['dates'] + [p.date.strftime("%d-%m-%y") for p in pr_data]))
            weights_my = {p.date.strftime("%d-%m-%y"): p.weight for p in pr_data}
            
            pr_plot_data = {
                'dates': dates_combined,
                'friend_weight': [pr_plot_data_friend['friend_weight'][pr_plot_data_friend['dates'].index(date)] if date in pr_plot_data_friend['dates'] else None for date in dates_combined],
                'my_weight': [weights_my[date] if date in weights_my else None for date in dates_combined],
            }
        else:
            pr_plot_data = pr_plot_data_friend

        # Serialize progression_plot_data for safe passage into the template
        serialized_pr_plot_data = json.dumps(pr_plot_data, cls=DjangoJSONEncoder)
        context = {
            'pr_plot_data': serialized_pr_plot_data,
        }
        return JsonResponse({"success": True, 'context': context})
    else:
        return JsonResponse({"success": False, "error": "Please provide a workout name."})


@login_required
def add_pr(request):
    form = PersonalRecordForm(request.POST)
    if form.is_valid():
        pr = form.save(commit=False)
        pr.user = request.user  # Set the current user
        check_if_pr(pr)
        
        # For AJAX request, return JSON response
        return JsonResponse({'status': 'success', 'message': 'PR added successfully'})
    else:
        # Handle invalid form for AJAX
        return JsonResponse({'status': 'error', 'errors': form.errors.as_json()}, status=400)
@login_required
def copy_workout(request, workout_id):
    try:
        friend_workout = WorkoutName.objects.get(id=workout_id)
        # Clone the workout
        my_workout = WorkoutName.objects.create(
            user=request.user,
            name=friend_workout.user.username+ "'s " + friend_workout.name + " (copy)"  # Modify name to indicate it's a copy
        )

        # Optionally, clone associated exercises if needed
        exercises = Exercise.objects.filter(name=friend_workout)
        for exercise in exercises:
            Exercise.objects.create(
                name=my_workout,
                exercise=exercise.exercise,
                reps=exercise.reps,
                sets=exercise.sets,
            )
        
        return JsonResponse({"success": True, "message": "Workout copied successfully!"})
    except WorkoutName.DoesNotExist:
        return JsonResponse({"success": False, "error": "Workout not found."}, status=404)
    
@login_required
def copy_own_workout(request, workout_id):
    try:
        my_own_workout = WorkoutName.objects.get(id=workout_id)
        # Clone the workout
        my_workout = WorkoutName.objects.create(
            user=request.user,
            name=my_own_workout.name + " (copy)"  # Modify name to indicate it's a copy
        )

        # Optionally, clone associated exercises if needed
        exercises = Exercise.objects.filter(name=my_own_workout)
        for exercise in exercises:
            Exercise.objects.create(
                name=my_workout,
                exercise=exercise.exercise,
                reps=exercise.reps,
                sets=exercise.sets,
            )
        
        return JsonResponse({"success": True, "message": "Workout copied successfully!"})
    except WorkoutName.DoesNotExist:
        return JsonResponse({"success": False, "error": "Workout not found."}, status=404)
    
@login_required
def food_view(request):
    # Your home page logic here
    return render(request, 'foods.html')

@login_required
def exercises(request):
    muscle_groups = ExerciseList.objects.values_list('muscle_group', flat=True).distinct().order_by('muscle_group')


    if request.method == 'POST':
        exercises_by_equipment = {}
        muscle_group = request.POST.get('muscle_group')

        exercises = ExerciseList.objects.filter(muscle_group=muscle_group).order_by('equipment', 'name')

        for exercise in exercises:
            if exercise.equipment in exercises_by_equipment:
                exercises_by_equipment[exercise.equipment].append(exercise)
            else:
                exercises_by_equipment[exercise.equipment] = [exercise]



        return render(request, 'exercises.html', {'exercises_by_equipment': exercises_by_equipment, 'muscle_groups': muscle_groups, 'current_group': muscle_group})
    return render(request, 'exercises.html', {'muscle_groups': muscle_groups})

@login_required
def profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    user_metrics = BodyMetric.objects.filter(user=request.user).order_by('-date').reverse() 

    muscle, fat, weight, bmi= get_metrics_list(user_metrics) 
    last_muscle = muscle[-1][0] if muscle else None
    last_fat = fat[-1][0] if fat else None
    last_weight = weight[-1][0] if weight else None
    last_bmi = bmi[-1][0] if bmi else None
    workout_stats = get_workout_stats_by_timeframe(request.user)
    stats = False
    for key, value in workout_stats.items():
        if value:
            stats = True


    return render(request, 'myprofile.html', {'profile': user_profile, 'workout_stats': workout_stats,'stats_available':stats, 'muscle': last_muscle, 'fat': last_fat, 'weight': last_weight, 'bmi': last_bmi})

@login_required
def update_muscle(request):

    if request.method == 'POST':

        BodyMetric.objects.create(
            user = request.user,
            muscle_percentage = request.POST.get('muscle_percentage'),
        )
  
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def update_fat(request):
    if request.method == 'POST':

        BodyMetric.objects.create(
            user = request.user,
            fat_percentage = request.POST.get('fat_percentage'),
        )
  
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def update_weight(request):
    if request.method == 'POST':

        BodyMetric.objects.create(
            user = request.user,
            weight = request.POST.get('weight'),
        )
  
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def get_muscle_data(request):
    # Assuming 'muscle' data is stored in user's profile and is accessible like this:
    user_metrics = BodyMetric.objects.filter(user=request.user).order_by('-date').reverse() 
    muscle_data, _, _, _= get_metrics_list(user_metrics) 

    data = {
        'dates': [dates.strftime("%d-%m-%y") for muscle, dates in muscle_data],
        'values': [muscle for muscle, dates  in muscle_data]
    }
    return JsonResponse(data)

@login_required
def get_fat_data(request):
    # Assuming 'muscle' data is stored in user's profile and is accessible like this:
    user_metrics = BodyMetric.objects.filter(user=request.user).order_by('-date').reverse() 
    _,fat_data, _, _= get_metrics_list(user_metrics) 

    data = {
        'dates': [dates.strftime("%d-%m-%y") for fat, dates in fat_data],
        'values': [fat for fat, dates in fat_data]
    }
    return JsonResponse(data)

@login_required
def get_weight_data(request):
    # Assuming 'muscle' data is stored in user's profile and is accessible like this:
    user_metrics = BodyMetric.objects.filter(user=request.user).order_by('-date').reverse() 
    _, _, weight_data, _= get_metrics_list(user_metrics) 

    data = {
        'dates': [dates.strftime("%d-%m-%y") for weight, dates in weight_data],
        'values': [weight for weight, dates in weight_data]
    }
    return JsonResponse(data)

@login_required
def get_bmi_data(request):
    # Assuming 'muscle' data is stored in user's profile and is accessible like this:
    user_metrics = BodyMetric.objects.filter(user=request.user).order_by('-date').reverse() 
    _, _, _, bmi_data= get_metrics_list(user_metrics) 
    data = {
        'dates': [dates.strftime("%d-%m-%y") for bmi, dates in bmi_data],
        'values': [bmi for bmi, dates in bmi_data]
    }
    return JsonResponse(data)


@login_required
def update_profile(request):
    if request.method == 'POST':
        profile = UserProfile.objects.get(user=request.user)
        user_metrics = BodyMetric.objects.filter(user=request.user).order_by('-date') 
        age = request.POST.get('age')
        if age:
            profile.age = age
        
        gender = request.POST.get('gender')
        if gender:
            profile.gender = gender

        length = request.POST.get('length')
        if length:
            profile.length = int(length)  # Convert to int, ensure this is safe with proper validation
            profile.save()
            update_bmis(user_metrics)   

        profile.save()
        return JsonResponse({
            'success': True,
            'profile': {
                'age': profile.age,
                'gender': profile.gender,
                'length': profile.length,
            }
        })
    return JsonResponse({'success': False})

@login_required
def update_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        image = request.FILES['profile_picture']
        processed_image = process_image(image)  # Use the process_image function we discussed earlier
        request.user.profile.profile_picture.save(processed_image.name, processed_image, save=True)
        return JsonResponse({'success': True, 'new_picture_url': request.user.profile.profile_picture.url})
    return JsonResponse({'success': False})

@login_required
def settings_view(request):

    usersettings = UserSettings.objects.get(user=request.user)

    if request.method == 'POST':
        session_info = request.POST.get('sessions')
        if session_info:
            session_info = True
        else:
            session_info = False
        
        personal_info = request.POST.get('personal_info')
        if personal_info:
            personal_info = True
        else:
            personal_info = False

        progress = request.POST.get('progress')
        if progress:
            progress = True
        else:
            progress = False

        usersettings.show_sessions = session_info
        usersettings.show_personal_info = personal_info
        usersettings.show_progress = progress
        usersettings.save()
        return redirect("myprofile")


    return render(request, 'settings.html', {'settings_user': usersettings})

def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect(reverse('login')) 

