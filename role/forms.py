from django import forms
from .models import Teacher, Student, Course


BRANCH_CHOICES = [
    ('coe', 'COE'),
    ('enc', 'ENC'),
    ('mec', 'MEC'),
    ('che','CHE')
]

YEAR_CHOICES = [
    ('1','1'),
    ('2','2'),
    ('3','3'),
    ('4','4')
]


class AddCourse(forms.Form):
    year = forms.IntegerField(choices=YEAR_CHOICES)
    branch = forms.IntegerField(max_length=5,choices=BRANCH_CHOICES)