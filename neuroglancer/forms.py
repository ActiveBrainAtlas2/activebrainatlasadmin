from django import forms


class AnimalChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.prep_id
