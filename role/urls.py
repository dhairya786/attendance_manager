from django.urls import path
from .views import home, register, dashboard, addcourse, CourseDetail
urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('dashboard/',dashboard, name='dashboard'),
    path('dashboard/addcourse',addcourse,name='addcourse'),
    path('dashboard/course<int:pk>',CourseDetail.as_view(),name='coursedetail')
]
