from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    path('api/send/', views.send_message, name='send_message'),
    path('api/delete/<int:conversation_id>/', views.delete_conversation, name='delete_conversation'),
    path('api/conversations/', views.get_conversations, name='get_conversations'),
]