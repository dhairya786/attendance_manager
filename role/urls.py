from django.urls import path
from .views import home, register, dashboard, addcourse, CourseDetail, profile, get_data, room, api, mycourses, pdfview, studymaterial, leaverequest, save, delete, marks
urlpatterns = [
    path('', home, name='home'),
    path('pdfview/',pdfview,name='pdfview'),
    path('register/', register, name='register'),
    path('dashboard/',dashboard, name='dashboard'),
    path('dashboard/addcourse',addcourse,name='addcourse'),
    path('dashboard/course<int:pk>',CourseDetail.as_view(),name='coursedetail'),
    path('dashboard/chart_data',get_data,name='chart_data'),
    path('profile/',profile,name='profile'),
    path('dashboard/course<int:pk>/room', room, name='room'),
    path('api/',api,name='api'),
    path('mycourses/',mycourses,name='mycourses'),
    path('dashboard/course<int:pk>/study',studymaterial,name='studymaterial'),
    path('dashboard/course<int:pk>/leave',leaverequest,name='leave'),
    path('save/',save,name="save"),
    path('delete/<int:course_pk>/<int:pk>/',delete,name="delete"),
    path('dashboard/course<int:pk>/marks/',marks,name='marks'),
]
