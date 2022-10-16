from django import forms
from .models import Project


class MissionPlannerForm(forms.Form):
    project       = forms.ModelChoiceField(queryset=Project.objects, label="Projeto")
    trip_weight   = forms.IntegerField(label="Peso da Tripulação", initial=300)
    takeoff_time  = forms.TimeField(label="Horário de DEP", initial='12:00')


class AirportInputField(forms.Form):
    icao_sign     = forms.CharField(max_length=4, label='', required=False)