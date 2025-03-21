from django.urls import path

from . import views

app_name = "application"
urlpatterns = [
    path('application', views.ApplicationView.as_view(), name='application'),
    path('application/<str:application_id>', views.ApplicationView.OperationView.as_view(), name='application_operation'),
    path('application/<str:application_id>/auth', views.ApplicationView.AthenticationView.as_view(), name='application_authentication'),
    path('application/<str:application_id>/chat', views.ApplicationView.ChatView.as_view(), name='application_chat'),
]
