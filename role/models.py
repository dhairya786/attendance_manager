from django.db import models
from django.contrib.auth.models import User
from django import template
from django.urls import reverse

register = template.Library()



# Create your models here.

BRANCH_CHOICES = [
    ('coe', 'COE'),
    ('enc', 'ENC'),
    ('mec', 'MEC'),
    ('che','CHE')
]



class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class Course(models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=100)
    teacher_assigned = models.ManyToManyField(Teacher, related_name='course')
    year = models.IntegerField(blank=True)
    branch = models.CharField(max_length=5,choices=BRANCH_CHOICES)
    image = models.ImageField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse('role:coursedetail',kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.name}"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email =models.EmailField(max_length=50)
    roll_no = models.BigIntegerField()
    course = models.ManyToManyField(Course, related_name='student', blank=True)
    image = models.ImageField(blank=True, null=True,default='default.png',upload_to='profile_pics/')


    def ismycourse(self,course):
        for c in self.course.all():
            if c is course:
                return True
        return False

    @register.filter
    def is_my_course(self, course):
        return self.ismycourse(course)

    def __str__(self):
        return f"{self.name}"


class Attendance(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    class_attended = models.IntegerField()
    total_classes = models.IntegerField()
    percentage = models.IntegerField(blank = True)

    class Meta:
        unique_together = (('course', 'student'),)


    def save(self, *args, **kwargs):
        if self.class_attended==0:
            self.percentage = 0;
        else:
            self.percentage = (self.class_attended)/(self.total_classes)*100
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} in {self.course}"

class AttendanceDetail(models.Model):
    attendance_field  = models.ForeignKey(Attendance,on_delete=models.CASCADE)
    date = models.DateField()
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.attendance_field.student.name} in {self.attendance_field.course.name} at {self.date}"

    class Meta:
        unique_together = (('attendance_field', 'date'),)
