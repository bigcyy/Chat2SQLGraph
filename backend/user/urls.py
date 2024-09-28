from django.urls import path

from . import views

app_name = "user"
urlpatterns = [
    path('user/login', views.LoginView.as_view(), name='login'),
    path('user/register', views.RegisterView.as_view(), name='register'),
    path('user/token', views.TokenView.as_view(), name='token'),
    path('user/hello', views.HelloView.as_view(), name='hello'),
]
