from django.urls import path
from .views import home, register, dashboard, addcourse
urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('dashboard/',dashboard, name='dashboard'),
    path('dashboard/addcourse',addcourse,name='addcourse')
]
