from django import forms
from .models import Section, Subject, Text

class SubjectForm(forms.ModelForm):

    class Meta:
        model = Subject
        fields = ['name', 'section']

class TextForm(forms.ModelForm):
    class Meta:
        model = Text
        fields = ['text']