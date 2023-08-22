from django import forms

class DateSelectionForm(forms.Form):
    desired_date = forms.DateField(label='Desired Date', widget=forms.DateInput(attrs={'type': 'date'}))
