from django import forms
from .models import Teacher, Student, Course, Leave


class StudentForm(forms.ModelForm): 
    class Meta: 
        model = Student 
        fields = ['name','email','image'] 


class DateInput(forms.DateInput):
    input_type = 'date'


class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['title','details','fro','to']
        widgets = {
            'fro': DateInput(attrs={'type': 'date'}),
            'to': DateInput(attrs={'type': 'date'})
        }
    def __init__(self, *args, **kwargs):
        super(LeaveForm, self).__init__(*args, **kwargs)
        self.fields['fro'].label = "From"




