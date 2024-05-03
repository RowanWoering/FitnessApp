from .models import *
from django.db.models import Max, Count, Avg
from django.shortcuts import get_object_or_404
import datetime
from django.utils import timezone
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO

def check_and_update_pr(user, exercise, reps, weight, session):

    current_pr = PersonalRecord.objects.filter(
        session=session,
        user=user,
        exercise=exercise,
        reps=reps
    ).aggregate(Max('weight'))

    max_weight = current_pr.get('weight__max')

    if max_weight is None or weight > max_weight:
        PersonalRecord.objects.update_or_create(
            user=user,
            session=session,
            exercise=exercise,
            reps=reps,
            date=session.date,
            defaults={'weight': weight}
        )

def get_aggregate_values(exercise):
    all_sets = exercise.set_list.all()
    weight = 0
    reps = 0
    partials = 0
    for set in all_sets:
        if set.weight:

            weight += float(set.weight)
        if set.reps:

            reps += float(set.reps)
        if set.partials:

            partials += float(set.partials)
    return weight, reps, partials


def calculate_progression_index(user, exercise, current_session):
    # Fetch the last session for the given exercise, excluding the current session

    last_session = Session.objects.filter(user=user, session_exercises__exercise=exercise, date__lt=current_session.date).order_by('-date').first()
    first_session = Session.objects.filter(user=user, session_exercises__exercise=exercise, date__lt=current_session.date).order_by('-date').last()
        
    user_metrics = BodyMetric.objects.filter(user=user).order_by('-date')

    muscle, fat, weight, bmi= get_metrics_list(user_metrics) 
    last_weight = weight[0][0] if weight else 0
    avg_weight = 75
    weight_ratio = (float(last_weight)/avg_weight)**0.3

    if last_session:

        # Fetch the details of the last session for normalization
        last_session_details = SessionExercise.objects.filter(session=last_session, exercise=exercise).first()
        first_session_details = SessionExercise.objects.filter(session=first_session, exercise=exercise).first()

        # Fetch the details of the current session
        current_session_details = SessionExercise.objects.filter(session=current_session, exercise=exercise).first()
        

        if current_session_details:
            POT=None
            PI=None
            current_weight, current_reps, current_partials = get_aggregate_values(current_session_details)
            W, R, P = 0.55, 0.4, 0.05
            if last_session_details:
            # Assuming you have a method or logic to calculate the sum or average of weights, reps, and partials
            # For the demonstration, let's assume you have a method to calculate these
                last_weight, last_reps, last_partials = get_aggregate_values(last_session_details)

                # Normalize current session values by last session values

                weight_normalized = (current_weight / last_weight)**2 if last_weight else 1
                reps_normalized = current_reps / last_reps if last_reps else 1
                partials_normalized = current_partials / last_partials if last_partials else 1


                # Calculate the Progression Index
                PI = ((W * weight_normalized) + (R * reps_normalized) + (P * partials_normalized))/weight_ratio

            if first_session_details:

                first_weight, first_reps, first_partials = get_aggregate_values(first_session_details)
                weight_normalized_ot = (current_weight / first_weight)**2 if first_weight else 1
                reps_normalized_ot = current_reps / first_reps if first_reps else 1
                partials_normalized_ot = current_partials / first_partials if first_partials else 1
                # Constants for weighting factors (assuming equal importance for demonstration)

                POT = ((W * weight_normalized_ot) + (R * reps_normalized_ot) + (P * partials_normalized_ot))/weight_ratio
            # Save or update the Progression Index in your model
            Progression.objects.update_or_create(
                user=user,
                exercise=exercise,
                session=current_session,
                date= current_session.date,
                defaults={'progression_index': PI,
                          'progression_over_time': POT}
            )
    else:
        Progression.objects.update_or_create(
            user=user,
            exercise=exercise,
            session=current_session,
            date= current_session.date,
            defaults={'progression_index': 1,
                        'progression_over_time': 1}
        )

def check_if_pr(pot_pr):
    pr_data = PersonalRecord.objects.filter(user=pot_pr.user, exercise=pot_pr.exercise, reps=pot_pr.reps).order_by('date')
    if(pr_data):
        if pr_data[0].weight<pot_pr.weight:
            pot_pr.save()
    else:
        pot_pr.save()

def count_workout_sessions(user):
    # Get the workout object based on the name and user
    workout_counts = WorkoutName.objects.filter(user=user, session__isnull=False).annotate(
        session_count=Count('session')
    ).order_by('-session_count')
    
    return workout_counts


def get_start_of_month(months_ago=0):
    today = timezone.now().date()
    first_day_this_month = today.replace(day=1)
    target_month = first_day_this_month - datetime.timedelta(days=30 * months_ago)
    start_of_target_month = target_month.replace(day=1)
    return start_of_target_month

def get_end_of_last_month():
    today = timezone.now().date()
    first_day_this_month = today.replace(day=1)
    end_of_last_month = first_day_this_month - datetime.timedelta(days=1)
    return end_of_last_month

def get_workout_stats_by_timeframe(user):
    timeframes = {
        'this month': (get_start_of_month(0), timezone.now().date()),
        'last month': (get_start_of_month(1), get_end_of_last_month()),
        'last three months': (get_start_of_month(3), get_end_of_last_month()),
        'last year': (get_start_of_month(12), get_end_of_last_month())
    }

    workout_stats = {}
    for timeframe, (start_date, end_date) in timeframes.items():
        workouts = WorkoutName.objects.filter(
            session__user=user,
            session__date__range=(start_date, end_date)
        ).annotate(
            session_count=Count('session'),
            avg_rating=Avg('session__rating')
        ).values('name', 'session_count', 'avg_rating')

        # Check for no data cases and set defaults
        workout_stats[timeframe] = [{
            'name': workout['name'],
            'session_count': workout['session_count'] if workout['session_count'] else 0,
            'avg_rating': "{:.2f}".format(workout['avg_rating']) if workout['avg_rating'] else "No Ratings"
        } for workout in workouts]

    return workout_stats


def process_image(image, width=250, height=350):
    # Open the uploaded image
    img = Image.open(image)
    if img.mode == 'RGBA':
        # Create a new white background image
        background = Image.new('RGB', img.size, (255, 255, 255))
        # Paste the image with alpha to the background
        background.paste(img, mask=img.split()[3])  # 3 is the index of the alpha channel in RGBA
        img = background
    # Calculate the crop size
    original_width, original_height = img.size
    target_ratio = height / width
    original_ratio = original_height / original_width

    if original_ratio > target_ratio:
        # Crop the height
        new_height = int(target_ratio * original_width)
        top = (original_height - new_height) / 2
        img = img.crop((0, top, original_width, top + new_height))
    else:
        # Crop the width
        new_width = int(original_height / target_ratio)
        left = (original_width - new_width) / 2
        img = img.crop((left, 0, left + new_width, original_height))
    
    # Resize to the target dimensions
    img = img.resize((width, height), Image.LANCZOS)

    # Save the cropped image to a BytesIO object
    img_io = BytesIO()
    img.save(img_io, format='JPEG', quality=100)

    # Create a new Django file-like object to save to the model
    new_image = ContentFile(img_io.getvalue(), name=image.name)
    return new_image

def get_metrics_list(x):
    muscle = []
    fat = []
    weigth = []
    bmi = []
    for metrics in x:
        if metrics.muscle_percentage:
            muscle.append((metrics.muscle_percentage, metrics.date))

        if metrics.fat_percentage:
            fat.append((metrics.fat_percentage, metrics.date))

        if metrics.weight:
            weigth.append((metrics.weight, metrics.date))
            bmi.append((metrics.bmi, metrics.date))
    return muscle, fat, weigth, bmi

def update_bmis(metrics):
    for x in metrics:
        if(x.weight):
            x.save()

    
