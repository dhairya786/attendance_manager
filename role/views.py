from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Student, Attendance, Course, AttendanceDetail, Studymaterial, Leave, Mark, Sgpa, Batch, Teacher
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from .utils import facestore, get_attendance_from_id, get_chart, take
from .forms import StudentForm, LeaveForm, TeacherForm, StudyForm
from django.views.generic.detail import DetailView
from attendance_management.settings import BASE_DIR
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.core.files import File  
import urllib
import datetime
from PIL import Image
import pandas as pd
import datetime
import json
import os
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from django.utils.safestring import mark_safe
from .serializers import StudentSerializer
from django.http import FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .thread import *
import smtplib
from django.core.mail import send_mail

# Create your views here.


def home(request):
    return render(request, 'role/index.html')


@api_view(['GET'])
def api(request):
    api_urls = {
        'register' :'register/',
        'CourseDetail' : 'dashboard/course<pk>',
    }
    std = Student.objects.all()
    serializer = StudentSerializer(std,many=True)
    return Response(serializer.data)

def register(request):
    counter=1
    if request.method == 'POST':
        if request.POST.get("Sign up"):
            uname = request.POST['username']
            rno = request.POST['rollno']
            name = request.POST['name']
            email = request.POST['email']
            password = request.POST['password']
            us = User.objects.create_user(uname, email, password)
            std = Student.objects.create(
                user=us, name=name, email=email, roll_no=rno)
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('register')
        if request.POST.get("Login"):
            username = request.POST['username']
            password = request.POST['password']
            print(username)
            print(password)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('dashboard')
            else:
                messages.success(request, f'Wrong Credentials')
    return render(request, 'role/register.html')

def dashboard(request):
    if request.method == 'POST':
        if request.POST.get("train"):
            facestore(request)
            Makedataset().start()
        if request.POST.get("course"):
            return redirect('addcourse')

    std = Student.objects.filter(user=request.user)
    att = Attendance.objects.filter(student=std[0])
    fro = timezone.now().date() - timedelta(days=7)
    to = timezone.now().date()
    count=0
    for sub in att:
        if sub.percentage<75:
            if sub.total_classes==0:
                continue
            count = count+1
    val = [] 
    finalval = []
    for st in std:
        for cou in st.course.all():
           val.append(cou)
    for item in val:
        att = Attendance.objects.filter(course = item,student = st)
        for ok in att:
            finalval.append(ok)
    cc = Course.objects.filter(student=std[0])
    name=""
    name1=""
    for c in cc:
        name = c.name
        break
    if cc.count() > 1:
        name1 = cc[1].name
    context = {
        'std' : std,
        'finalval' : finalval,
        'count' : count,
        'name' : name,
        'name1' : name1,
    }
    return render(request,'role/dashboard.html',context)

def get_data(request,*args,**kwargs):
    label1 = ["Present","Absent"] 
    std = Student.objects.filter(user=request.user)[0]
    cc = Course.objects.filter(student = std)
    data1 = []
    data2 = []
    date = datetime.date.today()
    for c in cc:
        att = Attendance.objects.filter(course=c,student=std)[0]
        details = AttendanceDetail.objects.filter(attendance_field=att)
        for d in details:
            obj = date-d.date
            if obj.days<= 1000:
                data2.append(d.status)
        data1.append(att.class_attended)
        data1.append(att.class_left)
        break
    label2 = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
    data3 = []
    if cc.count() > 1:
        att = Attendance.objects.filter(course = cc[1],student=std)[0]
        data3.append(att.class_attended)
        data3.append(att.class_left)
    data = {
     "data1" : data1,
     "label1" : label1,
     "data2" : data2,
     "label2" : label2,
     "customers" : 20,
     "data3" : data3, 
    }
    return JsonResponse(data)



def addcourse(request):
    mycourses = None  
    myenroll = []
    notenroll = []
    flag = False
    st = Student.objects.filter(user=request.user)
    if request.method == 'POST':
        if request.POST.get("wow"):
            year = request.POST['year']
            branch = request.POST['branch']
            mycourses = Course.objects.filter(year=year,branch=branch)
            for wow in st:
                stdenroll = wow.course.all()
                break
            for course in mycourses:
                for std in stdenroll:
                    if std.name==course.name:
                        myenroll.append(std)
                        flag = True
                        break
                if flag is not True:
                    notenroll.append(course)
                flag=False
        if request.POST.get("update"):
            mylist = request.POST.getlist("checkbox")
            print(mylist)
            if len(mylist)==0:
                return redirect('dashboard')
            for cc in st[0].course.all():
                st[0].course.remove(cc)
            for cou in mylist:
                objlist = Course.objects.filter(name=cou)
                obj = objlist[0]
                print(obj)
                st[0].course.add(obj)
                att = Attendance.objects.filter(course=obj,student=st[0])
                if len(att)==0:
                    newobj = Attendance.objects.create(course=obj,student=st[0],class_attended=0,total_classes=0)
                    newobj.save()
            return redirect('dashboard')
        if request.POST.get("remove"):
            print('working')
            for cc in st[0].course.all():
                st[0].course.remove(cc)
            return redirect('dashboard')
    
    context = {
        'myenroll' : myenroll,
        'notenroll' : notenroll,
        'std' : st,
    }  
    return render(request,'role/addcourse.html',context)

class CourseDetail(DetailView):
    def get(self,request,*args, **kwargs):
        pk = kwargs['pk']
        cc = Course.objects.get(id=pk)
        print(cc)
        st =Student.objects.filter(user=request.user)
        print(st[0])
        content= {
            'cc' : cc,
        }
        return render(request,'role/course_detail.html',content)
    def post(self,request,*args,**kwargs):
        fro = request.POST['from']
        to = request.POST['to']
        pk = kwargs['pk']
        cc = Course.objects.get(id=pk)
        st =Student.objects.filter(user=request.user)
        att = Attendance.objects.filter(course=cc,student=st[0])
        data = AttendanceDetail.objects.filter(date__range=[fro,to],attendance_field=att[0])
        content= {
            'cc' : cc,
            'data' : data,
            'att' : att,
        }
        return render(request,'role/course_detail.html',content)

def room(request, *args,**kwargs):
    pk = kwargs['pk']
    cc = Course.objects.get(id=pk)
    return render(request, 'role/timepass.html', {
        'room_name': cc,
        'room_id' : pk,
        'username' : request.user.username,
        'cc' : cc,
    })

def profile(request):
    if request.method=='POST':
        st =Student.objects.filter(user=request.user)
        form = StudentForm(request.POST,request.FILES,instance = st[0],initial={'name': st[0].name})
        if form.is_valid():
            form.save()
    else :
        st =Student.objects.filter(user=request.user)
        form = StudentForm(instance = st[0])
    context = {
        'st' : st[0],
        'form' : form
    }        
    return render(request,'role/profile.html',context)


def mycourses(request):
    st = Student.objects.filter(user=request.user)[0]  
    att = Attendance.objects.filter(student = st)
        
    context = {
    'st' : st,
    'att' : att,
    }
    return render(request,'role/mycourse.html',context)

def studymaterial(request,*args,**kwargs):
    pk = kwargs['pk']
    cc = Course.objects.get(id=pk)
    mat = Studymaterial.objects.filter(course=cc)
    return render(request,'role/study.html',{
        'mat' : mat,
        'cc' : cc,
        })


def pdfview(request):
    try:
        print('in hu saale')
        return FileResponse(open('study_material/CPG123.pdf', 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()

def leaverequest(request,*args,**kwargs):
    pk = kwargs['pk']
    cc = Course.objects.get(id=pk)
    std = Student.objects.filter(user=request.user)[0]
    leave = Leave.objects.filter(student = std, course = cc).order_by('fro').reverse()
    leaveform = LeaveForm()
    context = {
    'leave' : leave,
    'std' : std,
    'cc' : cc,
    'form' : leaveform,
    }
    return render(request,'role/leave.html',context)

@csrf_exempt
def save(request):
    print('good')
    data = json.loads(request.body)
    st = Student.objects.get(id=data['student'])
    cc = Course.objects.get(id=data['course'])
    obj = Leave.objects.create(student = st,course=cc,title=data['title'],details=data['details'],fro=data['fro'],to=data['to'])
    obj.save()
    return JsonResponse({
        "msg" : "success"
        })


def delete(request, *args,**kwargs):
    print(kwargs)
    lpk = kwargs['pk']
    post = Leave.objects.get(pk=lpk).delete()
    cpk = kwargs['course_pk']
    return redirect('leave',pk=cpk)


def marks(request,*args,**kwargs):
    pk = kwargs['pk']
    cc = Course.objects.get(id=pk)
    std = Student.objects.filter(user=request.user)[0]
    mark = Mark.objects.filter(student=std,course=cc)
    context = {
    'cc' : cc,
    'mark' : mark,
    }
    return render(request,'role/marks.html',context)


def cgpa(request):
    std = Student.objects.filter(user=request.user)[0]
    sg = Sgpa.objects.filter(student = std)
    mysum=0
    myval=0
    for s in sg:
        myval = myval + 1
        mysum = mysum + s.sgpa
    if myval != 0:
        mysum = mysum/myval
        mysum = round(mysum,2)
    print(mysum)
    context = {
    'std' : std,
    'sg' : sg,
    'mysum' : mysum,
    }
    return render(request,'role/cgpa.html',context)


def registerteacher(request):
    if request.method == 'POST':
        if request.POST.get("Login"):
            username = request.POST['username']
            password = request.POST['password']
            print(username)
            print(password)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('dashboardteacher')
            else:
                messages.success(request, f'Wrong Credentials')
    return render(request,'role/registerteacher.html')

def dashboardteacher(request):
    teacher = Teacher.objects.filter(user=request.user)[0]
    b= Batch.objects.filter(teacher = teacher)
    cc = Course.objects.filter(teacher_assigned=teacher)[0]
    students = []
    batches= []
    d = datetime.datetime.now().date()
    for bb in b:
        for s in bb.student.all():
            students.append(s)
            batches.append(bb)

    if request.method == 'POST':
        print(request.POST)
        if request.POST.get("notify"):
            Sendmail(teacher).start()
        if request.POST.get("train"):
            print('good')
            take(request)
            return redirect('markedstudent')

    data = zip(students,batches)
    course = Course.objects.filter(teacher_assigned=teacher)[0]
    print(course)
    context = {
    'students' : students, 
    'batches' : batches,
    'data': data,
    'course': course,
    }
    return render(request,'role/dashboardteacher.html',context)


def manualteacher(request):
    students = []
    teacher = Teacher.objects.filter(user=request.user)[0]
    cc = Course.objects.filter(teacher_assigned=teacher)[0]
    d = datetime.datetime.now().date()
    print(d)
    if request.method == 'POST':
        if request.POST.get("wow"):
            b = request.POST['batch']
            bb = Batch.objects.get(pk = b)
            for s in bb.student.all():
                students.append(s)
        if request.POST.get("update"):
            mylist = request.POST.getlist("checkbox")
            if len(mylist) != 0:
                s = Student.objects.get(pk = mylist[0])
                b = Batch.objects.filter(student = s)[0]
                for s in b.student.all():
                    print(s)
                    att = Attendance.objects.filter(student = s,course = cc)[0]
                    det = AttendanceDetail.objects.filter(attendance_field=att,date__year = d.year,date__month = d.month,date__day = d.day)
                    if(det.count()== 0):
                        obj = AttendanceDetail.objects.create(attendance_field=att,date = d,status = False)
                        att.save()
                        obj.save()
                    else:
                        oo = det.last()
                        oo.status = False
                        oo.save()
                        print(oo.status)
            for pp in mylist:
                st = Student.objects.get(pk = pp)
                att = Attendance.objects.filter(student = st,course = cc)[0]
                det = AttendanceDetail.objects.filter(attendance_field=att,date__year = d.year,date__month = d.month,date__day = d.day)
                oo = det.last()
                oo.status = True
                oo.save()
                print(oo)
                print(att.class_attended)

            if len(mylist) != 0:
                s = Student.objects.get(pk = mylist[0])
                b = Batch.objects.filter(student = s)[0]
                for s in b.student.all():
                    att = Attendance.objects.filter(student = s,course = cc)[0]
                    det = AttendanceDetail.objects.filter(attendance_field=att)
                    count=0
                    tot = 0
                    for obj in det:
                        if obj.status:
                            count = count+1
                        tot = tot+1
                    att.class_attended = count
                    att.total_classes = tot
                    att.save()

    b = Batch.objects.filter(teacher= teacher)
    batches = []
    for bb in b:
        batches.append(bb)
    present = []
    absent = []
    for s in students:
        att = Attendance.objects.filter(student = s,course = cc)[0]
        det = AttendanceDetail.objects.filter(attendance_field=att,date__year = d.year,date__month = d.month,date__day = d.day)
        if(det.count()==0):
            absent.append(s)
        else:
            oo = det.last()
            if(oo.status):
                present.append(s)
            else:
                absent.append(s)


    context = {
    'batches' : batches,
    'students' : students,
    'present' : present,
    'absent' : absent,
    }
    return render(request,'role/manualteacher.html',context)



def teacherroom(request):
    teacher = Teacher.objects.filter(user=request.user)[0]
    cc = Course.objects.filter(teacher_assigned=teacher)[0]
    pk = cc.id
    return render(request, 'role/room.html', {
        'room_name': cc,
        'room_id' : pk,
        'username' : request.user.username,
        'cc' : cc,
    })
        

def teacherleave(request):
    teacher = Teacher.objects.filter(user=request.user)[0]
    cc = Course.objects.filter(teacher_assigned=teacher)[0]
    students = []
    b= Batch.objects.filter(teacher = teacher)
    for bb in b:
        for s in bb.student.all():
            students.append(s)
    leave = []
    for s in students:
        ll = Leave.objects.filter(student = s).order_by('fro').reverse()
        for l in ll:
            leave.append(l)
    print(leave)

    context = {
    'cc' : cc,
    'leave' : leave,
    }
    return render(request,'role/teacherleave.html',context)


def viewleave(request, *args,**kwargs):
    lpk = kwargs['pk']
    cpk = kwargs['course_pk']
    leave = Leave.objects.get(pk = lpk)
    if request.method == 'POST':
        if request.POST.get('approve'):
            print('approve')
            leave.isapproved = 1
            leave.save()
            return redirect('teacherleave')
        if request.POST.get('disapprove'):
            print('disapprove')
            leave.isapproved = -1
            leave.save()
            return redirect('teacherleave')
    return render(request,'role/viewleave.html',{'leave' : leave})


def teacherprofile(request):
    if request.method=='POST':
        teacher = Teacher.objects.filter(user=request.user)[0]
        form = TeacherForm(request.POST,request.FILES,instance = teacher,initial={'name': teacher.name})
        if form.is_valid():
            form.save()
    else :
        teacher =Teacher.objects.filter(user=request.user)[0]
        form = TeacherForm(instance = teacher)
    context = {
        'teacher' : teacher,
        'form' : form
    }        
    return render(request,'role/teacherprofile.html',context)


def teacherpdf(request):
    teacher = Teacher.objects.filter(user=request.user)[0]
    cc = Course.objects.filter(teacher_assigned=teacher)[0]
    mat = Studymaterial.objects.filter(course=cc)
    context = {
    'cc' : cc,
    'mat' : mat,
    }
    return render(request,'role/teacherpdf.html',context)

def teacherupload(request, *args, **kwargs):
    cpk = kwargs['pk']
    cc = Course.objects.get(pk = cpk)
    form = StudyForm(initial={'course' : cc})
    context = {
    'form' : form,
    }
    if request.method=='POST':
        form = StudyForm(request.POST,request.FILES,initial={'course': cc})
        if form.is_valid():
            form.save()
        return redirect('teacherpdf')
    return render(request,'role/teacherupload.html',context)


def markedstudent(request):
    teacher = Teacher.objects.filter(user=request.user)[0]
    cc = Course.objects.filter(teacher_assigned=teacher)[0]
    b= Batch.objects.filter(teacher = teacher)
    students = []
    batches= []
    d = datetime.datetime.now().date()
    for bb in b:
        for s in bb.student.all():
            students.append(s)
    finalstudents = []
    pk = request.user.pk
    src = []
    mylist = Attendancepic.objects.filter(teacher=teacher)
    print(mylist)
    for i in range(6):
        src.append(str(pk)+'_'+str(i))
    print(src)
    for s in students:
        att = Attendance.objects.filter(student = s,course = cc)[0]
        det = AttendanceDetail.objects.filter(attendance_field=att,date__year = d.year,date__month = d.month,date__day = d.day)
        if(det.count()!=0):
            oo = det.last()
            if(oo.status):
                finalstudents.append(s)
    context = {
        'finalstudents' : finalstudents,
        'src' : src,
        'user' : request.user.pk,
        'mylist' : mylist,
    }
    Sendmail(teacher).start()
    return render(request,'role/markedstudent.html',context)







