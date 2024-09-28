from django.urls import path, include
from user import views as auth_views

urlpatterns = [
    path("api/", include("user.urls")),
    path("api/", include("setting.urls")),
    path("api/", include("chat.urls")),
]