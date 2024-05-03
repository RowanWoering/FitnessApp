from django.contrib import admin
from .models import *

admin.site.register(WorkoutName)
admin.site.register(Exercise)
admin.site.register(Session)
admin.site.register(SessionExercise)
admin.site.register(SessionExerciseSet)
admin.site.register(ExerciseList)
admin.site.register(CustomExerciseList)
admin.site.register(Friendship)
admin.site.register(FriendRequest)
admin.site.register(PersonalRecord)
admin.site.register(Progression)
admin.site.register(UserProfile)
admin.site.register(BodyMetric)
admin.site.register(UserSettings)
# Register your models here.
