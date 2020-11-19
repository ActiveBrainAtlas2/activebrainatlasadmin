from django import forms
from django.forms import ModelChoiceField



class AnimalChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.prep_id
