from django.urls import path

from . import views

app_name = "application"
urlpatterns = [
    path('application', views.ApplicationView.as_view(), name='application'),
]
