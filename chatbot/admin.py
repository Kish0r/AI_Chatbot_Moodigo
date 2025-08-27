# chatbot/admin.py
from django.contrib import admin
from .models import *

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'is_anonymous', 'created_at', 'last_activity']
    list_filter = ['is_anonymous', 'created_at']
    search_fields = ['session_id', 'user__username']
    readonly_fields = ['session_id', 'created_at']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'title', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'session__session_id']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'predicted_condition', 'confidence_score', 'timestamp']
    list_filter = ['sender', 'predicted_condition', 'timestamp']
    search_fields = ['content', 'conversation__session__session_id']
    readonly_fields = ['timestamp']

@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'mood', 'intensity', 'created_at']
    list_filter = ['mood', 'intensity', 'created_at']
    search_fields = ['session__session_id', 'notes']
    readonly_fields = ['created_at']

@admin.register(MentalHealthAssessment)
class MentalHealthAssessmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'risk_level', 'total_score', 'created_at']
    list_filter = ['risk_level', 'created_at']
    search_fields = ['session__session_id']
    readonly_fields = ['created_at']

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource_type', 'is_crisis', 'is_active', 'created_at']
    list_filter = ['resource_type', 'is_crisis', 'is_active', 'created_at']
    search_fields = ['title', 'description']

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['session', 'preferred_name', 'university', 'enable_mood_tracking', 'crisis_mode']
    list_filter = ['enable_mood_tracking', 'daily_check_ins', 'crisis_mode']
    search_fields = ['session__session_id', 'preferred_name', 'university']