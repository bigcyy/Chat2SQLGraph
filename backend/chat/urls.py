from django.urls import path

from . import views

app_name = "chat"
urlpatterns = [
    path('chat', views.ChatView.as_view(), name='chat'),
    path('chat/<str:datasource_id>', views.ChatView.as_view(), name='chat_with_datasource_id'),
    path('chat/<str:datasource_id>/<str:chat_id>', views.ChatView.MessageView.as_view(), name='message'),
]
