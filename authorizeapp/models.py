from django.db import models
from django.conf import settings
from django.db.models import Max
from django.core.validators import MinValueValidator, MaxValueValidator
import os

# Create your models here.
class WorkoutName(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workouts')
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

class Exercise(models.Model):
    name = models.ForeignKey(WorkoutName, on_delete=models.CASCADE)
    exercise = models.CharField(max_length=200)
    reps = models.IntegerField()
    sets = models.IntegerField()

    def __str__(self):
        return f"{self.exercise} - {self.name.user.username}"
    
class Session(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    name = models.CharField(max_length=200)
    workout = models.ForeignKey(WorkoutName, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])


    def __str__(self):
        return f"{self.name} on {self.date} - {self.user.username}"

class SessionExercise(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='session_exercises')
    exercise = models.CharField(max_length=200)  # Renamed for clarity
    reps = models.IntegerField()
    sets = models.IntegerField()
    # exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.exercise} - {self.session.user.username}"
    
class SessionExerciseSet(models.Model):
    session_exercise = models.ForeignKey(SessionExercise, related_name='set_list', on_delete=models.CASCADE)
    set = models.IntegerField()
    reps = models.IntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=1)
    partials = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.set} - {self.session_exercise} - {self.session_exercise.session.user.username}"

class ExerciseList(models.Model):
    name = models.CharField(max_length=255)
    muscle_group = models.CharField(max_length=255, blank=True, null=True)
    equipment = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"
    
class CustomExerciseList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='custom_exercises')
    name = models.CharField(max_length=255)
    muscle_group = models.CharField(max_length=255, blank=True, null=True)
    equipment = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
class Friendship(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="friendship_creator", on_delete=models.CASCADE)
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="friend", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('creator', 'friend')

    def __str__(self):
        return f"{self.creator} is friends with {self.friend}"
    
class FriendRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend_requests_sent', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend_requests_received', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"Friend request from {self.sender} to {self.receiver}"
    
class PersonalRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exercise = models.CharField(max_length=200)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, blank=True)
    reps = models.IntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.exercise}with {self.weight}kgs for {self.reps} reps - {self.user.username}"

class Progression(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exercise = models.CharField(max_length=200)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    progression_index = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    progression_over_time = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    date = models.DateField()

    def __str__(self):
        return f"{self.exercise} progression - {self.user.username}"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True, default='profile_pics/fitness_img.png', max_length=1024*1024)
    favorite_exercise = models.CharField(max_length=100, null=True, blank=True)
    length = models.IntegerField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    gender = models.CharField(max_length=30, null=True, blank=True, choices=GENDER_CHOICES)

    def save(self, *args, **kwargs):
        # Delete old file when replacing it with a new one
        try:
            this = UserProfile.objects.get(id=self.id)
            if this.profile_picture != self.profile_picture:
                if this.profile_picture:
                    os.remove(this.profile_picture.path)
        except:
            pass  # when new photo then we do nothing, normal case

        super(UserProfile, self).save(*args, **kwargs)

    # Additional fields as necessary

    def __str__(self):
        return f'{self.user.username} Profile'
    
class BodyMetric(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='body_metrics')
    date= models.DateField(auto_now_add=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    muscle_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fat_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    bmi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    def save(self, *args, **kwargs):
        if self.weight and self.user.profile.length:  # Ensure weight and height are available
            print(self.weight)
            height_in_meters = int(self.user.profile.length) / 100  # Assuming height is stored in centimeters
            print(height_in_meters)
            self.bmi = (float(self.weight) / (height_in_meters ** 2))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s health data for {self.date}"
    
class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='setting_view')
    show_sessions = models.BooleanField(default=True)
    show_personal_info = models.BooleanField(default=True)
    show_progress= models.BooleanField(default=True)
    # Additional fields as necessary

    def __str__(self):
        return f'{self.user.username} Settings'
