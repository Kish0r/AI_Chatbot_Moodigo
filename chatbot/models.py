# chatbot/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class UserSession(models.Model):
    """Track anonymous user sessions"""
    session_id = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_anonymous = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Session {self.session_id[:8]}"

class Conversation(models.Model):
    """Store chat conversations"""
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Conversation {self.id} - {self.created_at.strftime('%Y-%m-%d')}"

class Message(models.Model):
    """Individual chat messages"""
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]
    
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # ML Model predictions
    predicted_condition = models.CharField(max_length=50, blank=True, null=True)
    confidence_score = models.FloatField(blank=True, null=True)
    risk_level = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender}: {self.content[:50]}..."

class MoodEntry(models.Model):
    """Track user mood over time"""
    MOOD_CHOICES = [
        ('very_happy', '😄 Very Happy'),
        ('happy', '😊 Happy'),
        ('neutral', '😐 Neutral'),
        ('sad', '😞 Sad'),
        ('very_sad', '😢 Very Sad'),
        ('anxious', '😰 Anxious'),
        ('stressed', '😤 Stressed'),
        ('angry', '😠 Angry'),
    ]
    
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE)
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    intensity = models.IntegerField(choices=[(i, str(i)) for i in range(1, 11)])  # 1-10 scale
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_mood_display()} ({self.intensity}/10) - {self.created_at.strftime('%Y-%m-%d')}"

class MentalHealthAssessment(models.Model):
    """Store mental health survey responses"""
    RISK_LEVELS = [
        ('low', 'Low Risk'),
        ('moderate', 'Moderate Risk'),
        ('high', 'High Risk'),
        ('very_high', 'Very High Risk'),
    ]
    
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE)
    total_score = models.IntegerField()
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS)
    responses = models.JSONField()  # Store all survey responses
    created_at = models.DateTimeField(auto_now_add=True)
    recommendations = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Assessment {self.id} - {self.get_risk_level_display()}"

class Resource(models.Model):
    """Mental health resources"""
    RESOURCE_TYPES = [
        ('crisis', 'Crisis Support'),
        ('counseling', 'Counseling Services'),
        ('app', 'Mobile App'),
        ('article', 'Article/Guide'),
        ('hotline', 'Hotline'),
        ('exercise', 'Mental Exercise'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    url = models.URLField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_crisis = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class UserPreference(models.Model):
    """User preferences and settings"""
    session = models.OneToOneField(UserSession, on_delete=models.CASCADE)
    enable_mood_tracking = models.BooleanField(default=True)
    daily_check_ins = models.BooleanField(default=False)
    crisis_mode = models.BooleanField(default=False)
    preferred_name = models.CharField(max_length=50, blank=True)
    university = models.CharField(max_length=100, blank=True)
    year_of_study = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"Preferences for {self.session.session_id[:8]}"