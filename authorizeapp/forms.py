from django.forms import ModelForm, Select, ChoiceField, Form
from .models import *
import datetime

 

class ExerciseForm(ModelForm):
    class Meta:
        model = Exercise
        exclude = ['name']

class WorkoutForm(ModelForm):
    class Meta:
        model = WorkoutName
        fields = ['name']

from .models import Session

class SessionForm(ModelForm):
    class Meta:
        model = Session
        fields = ['date', 'name', 'workout']
        widgets = {
            'workout': Select()
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(SessionForm, self).__init__(*args, **kwargs)
        self.fields['workout'].queryset = WorkoutName.objects.filter(user=user)


class PersonalRecordForm(ModelForm):
    class Meta:
        model = PersonalRecord
        fields = ['exercise', 'reps', 'weight', 'date']



class MonthFilterForm(Form):
    current_year = datetime.date.today().year
    current_month = datetime.date.today().month

    year = ChoiceField(choices=[(year, year) for year in range(2023, 2050)], required=False, label='Year')  # Example range
    month = ChoiceField(choices=[
        (1, "January"), (2, "February"), (3, "March"), (4, "April"),
        (5, "May"), (6, "June"), (7, "July"), (8, "August"),
        (9, "September"), (10, "October"), (11, "November"), (12, "December")
    ], required=False, label='Month')

    def __init__(self, *args, **kwargs):
        super(MonthFilterForm, self).__init__(*args, **kwargs)
        self.fields['year'].initial = self.current_year
        self.fields['month'].initial = self.current_month
        self.fields['year'].widget.attrs.update({'class': 'form-control'})
        self.fields['month'].widget.attrs.update({'class': 'form-control'})

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']

class MuscleGroupForm(Form):
    muscle_group = ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['muscle_group'].choices = [(mg, mg) for mg in ExerciseList.objects.values_list('muscle_group', flat=True).distinct()]
