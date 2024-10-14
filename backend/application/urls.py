from django.urls import path

from . import views

app_name = "application"
urlpatterns = [
    path('application', views.ApplicationView.as_view(), name='application'),
    path('application/<str:application_id>', views.ApplicationView.OperationView.as_view(), name='application_operation'),
]
