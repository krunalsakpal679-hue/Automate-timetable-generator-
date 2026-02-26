# timetable_project/scheduler/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('regenerate/', views.regenerate_timetable, name='regenerate_timetable'),
    path("download-pdf/", views.download_timetable_pdf, name="download_timetable_pdf"),
]
