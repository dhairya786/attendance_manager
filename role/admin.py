from django.contrib import admin
from .models import *


class StudentAdmin(admin.ModelAdmin):
	list_display = ['name', 'user', ]
	filter_fields = ['course']
# Register your models here.
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(Student,StudentAdmin)
admin.site.register(Attendance)
admin.site.register(AttendanceDetail)
admin.site.register(Message)
admin.site.register(Studymaterial)
admin.site.register(Leave)
admin.site.register(Mark)
admin.site.register(Sgpa)
admin.site.register(Batch)
admin.site.register(Attendancepic)