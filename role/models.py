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

FIELD_CHOICES = [
    ('LE1','LE1'),
    ('LE2','LE2'),
    ('LE3','LE3'),
    ('SES1','SES1'),
    ('SES2','SES2'),
    ('SES3','SES3'),
    ('MST','MST'),
    ('EST','EST'),
]



class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(blank=True, null=True,default='default.png',upload_to='profile_pics/')


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

class Batch(models.Model):
    name = models.CharField(max_length=100)
    student = models.ManyToManyField(Student,null=True,blank=True)
    teacher = models.ManyToManyField(Teacher,null=True,blank=True)

    def __str__(self):
        return f"{self.name}"


class Attendance(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    class_attended = models.IntegerField()
    total_classes = models.IntegerField()
    class_left = models.IntegerField(blank=True,null=True)
    percentage = models.IntegerField(blank = True)

    class Meta:
        unique_together = (('course', 'student'),)


    def save(self, *args, **kwargs):
        if self.class_attended==0:
            self.percentage = 0;
        else:
            self.percentage = (self.class_attended)/(self.total_classes)*100
        self.class_left = self.total_classes - self.class_attended
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

class Message(models.Model):
    author = models.ForeignKey(User,related_name='author_messages',on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)

    class Meta:
        unique_together = (('author', 'timestamp'),)

    def __str__(self):
        return f"{self.author.username}"

    def last_10_messages(self):
        return Message.objects.order_by('-timestamp').all()[:10]

class Studymaterial(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    file = models.FileField(upload_to='study_material/')
    video = models.BooleanField(null=True,default=False)

    def __str__(self):
        return self.title

class Leave(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    title = models.CharField(max_length = 30)
    details = models.TextField()
    isapproved = models.IntegerField(default=0)
    fro = models.DateField(null=True)
    to = models.DateField(null=True)
    def __str__(self):
        return f"{self.student.name} - {self.title} - {self.course.name}" 


class Mark(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    obtained = models.IntegerField()
    total = models.IntegerField()
    field = models.CharField(max_length=30,choices=FIELD_CHOICES)

    def __str__(self):
        return f"{self.student.name} in {self.course.name} for {self.field}"

class Sgpa(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    semester = models.IntegerField()
    sgpa = models.DecimalField(max_digits = 7,decimal_places=2)

    def __str__(self):
        return f"{self.student.name} got {self.sgpa} in {self.semester} semester"


class Attendancepic(models.Model):
    number = models.IntegerField()
    teacher = models.ForeignKey(Teacher,on_delete=models.CASCADE)
    image = models.ImageField(blank=True,null=True,upload_to='attendance_pics/')

    def __str__(self):
        return f"{self.number} of {self.teacher.name}"


