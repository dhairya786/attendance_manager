from django import forms
from .models import Teacher, Student, Course, Leave, Studymaterial


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



class TeacherForm(forms.ModelForm): 
    class Meta: 
        model = Teacher 
        fields = ['name','image']


class StudyForm(forms.ModelForm):
    class Meta:
        model = Studymaterial
        fields = ['course','title','file','video']




