# chatbot/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('chat/', views.chat, name='chat'),
    path('mood-tracker/', views.mood_tracker, name='mood_tracker'),
    path('assessment/', views.assessment, name='assessment'),
    path('resources/', views.resources, name='resources'),
    path('crisis-help/', views.crisis_help, name='crisis_help'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('terms/', views.terms_of_service, name='terms'),
    

    
    # Chat functionality
    path('send-message/', views.send_message, name='send_message'),
    path('new-conversation/', views.new_conversation, name='new_conversation'),
    
    # History and conversations
    path('history/', views.conversation_history, name='conversation_history'),
    path('conversation/<int:conversation_id>/', views.view_conversation, name='view_conversation'),
    
    # AJAX endpoints
    path('mood-chart-data/', views.mood_chart_data, name='mood_chart_data'),
]