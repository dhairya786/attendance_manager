from django.urls import path
from .views import home, register, dashboard, addcourse, CourseDetail, profile, get_data
urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('dashboard/',dashboard, name='dashboard'),
    path('dashboard/addcourse',addcourse,name='addcourse'),
    path('dashboard/course<int:pk>',CourseDetail.as_view(),name='coursedetail'),
    path('dashboard/chart_data',get_data,name='chart_data'),
    path('profile',profile,name='profile')
]
