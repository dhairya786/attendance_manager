from django import forms
from .models import Teacher, Student, Course


class StudentForm(forms.ModelForm): 
    class Meta: 
        model = Student 
        fields = ['name','email','image'] 




