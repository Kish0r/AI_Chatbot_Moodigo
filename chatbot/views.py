# chatbot/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import *
from .ml_models import MoodigoAI
from .forms import MoodEntryForm, SurveyForm
import json
import uuid
from datetime import datetime, timedelta

# Initialize AI service
moodigo_ai = MoodigoAI()
moodigo_ai.initialize()

def get_or_create_session(request):
    """Get or create user session for anonymous users"""
    session_id = request.session.get('session_id')
    
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session['session_id'] = session_id
    
    user_session, created = UserSession.objects.get_or_create(
        session_id=session_id,
        defaults={
            'user': request.user if request.user.is_authenticated else None,
            'is_anonymous': not request.user.is_authenticated
        }
    )
    
    if not created:
        user_session.last_activity = timezone.now()
        user_session.save()
    
    return user_session

def home(request):
    """Homepage view"""
    return render(request, 'chatbot/home.html')

def about(request):
    """About page view"""
    return render(request, 'chatbot/about.html')

def chat(request):
    """Main chat interface"""
    user_session = get_or_create_session(request)
    
    # Get or create active conversation
    conversation = Conversation.objects.filter(
        session=user_session, 
        is_active=True
    ).first()
    
    if not conversation:
        conversation = Conversation.objects.create(
            session=user_session,
            title=f"Chat {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        )
    
    # Get recent messages
    messages = conversation.messages.all()[:50]  # Last 50 messages
    
    context = {
        'conversation': conversation,
        'messages': messages,
        'session_id': user_session.session_id
    }
    
    return render(request, 'chatbot/chat.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """Handle chat messages via AJAX"""
    try:
        data = json.loads(request.body)
        message_content = data.get('message', '').strip()
        
        if not message_content:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        user_session = get_or_create_session(request)
        
        # Get or create conversation
        conversation = Conversation.objects.filter(
            session=user_session,
            is_active=True
        ).first()
        
        if not conversation:
            conversation = Conversation.objects.create(
                session=user_session,
                title=f"Chat {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            )
        
        # Save user message
        user_message = Message.objects.create(
            conversation=conversation,
            sender='user',
            content=message_content
        )
        
        # Analyze message with AI
        ai_analysis = moodigo_ai.analyze_message(message_content)
        
        # Generate bot response
        bot_response = ai_analysis['response']
        
        # Save bot message with AI predictions
        bot_message = Message.objects.create(
            conversation=conversation,
            sender='bot',
            content=bot_response,
            predicted_condition=ai_analysis['prediction'],
            confidence_score=ai_analysis['confidence']
        )
        
        # Check if this is a crisis situation
        is_crisis = ai_analysis['prediction'] == 'Suicidal' or (
            ai_analysis['prediction'] == 'Depression' and ai_analysis['confidence'] > 0.8
        )
        
        # Update user preferences if crisis detected
        if is_crisis:
            preferences, _ = UserPreference.objects.get_or_create(session=user_session)
            preferences.crisis_mode = True
            preferences.save()
        
        response_data = {
            'bot_response': bot_response,
            'prediction': ai_analysis['prediction'],
            'confidence': ai_analysis['confidence'],
            'is_crisis': is_crisis,
            'timestamp': bot_message.timestamp.strftime('%H:%M')
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def mood_tracker(request):
    """Mood tracking page"""
    user_session = get_or_create_session(request)
    
    if request.method == 'POST':
        form = MoodEntryForm(request.POST)
        if form.is_valid():
            mood_entry = form.save(commit=False)
            mood_entry.session = user_session
            mood_entry.save()
            messages.success(request, 'Mood entry saved successfully!')
            return redirect('mood_tracker')
    else:
        form = MoodEntryForm()
    
    # Get recent mood entries
    mood_entries = MoodEntry.objects.filter(session=user_session)[:30]
    
    # Generate mood insights
    mood_insights = moodigo_ai.get_mood_insights(mood_entries)
    
    context = {
        'form': form,
        'mood_entries': mood_entries,
        'mood_insights': mood_insights
    }
    
    return render(request, 'chatbot/mood_tracker.html', context)

def assessment(request):
    """Mental health survey/assessment"""
    user_session = get_or_create_session(request)
    
    # Mental health questions (simplified version)
    questions = [
        "How often do you feel nervous or anxious?",
        "How often do you feel depressed or down?",
        "How often do you have trouble sleeping?",
        "How often do you feel overwhelmed by daily tasks?",
        "How often do you feel hopeless about the future?",
        "How often do you have difficulty concentrating?",
        "How often do you feel tired or have little energy?",
        "How often do you feel bad about yourself?",
        "How often do you feel restless or fidgety?",
        "How often do you have thoughts of self-harm?"
    ]
    
    if request.method == 'POST':
        # Process survey responses
        responses = {}
        for i, question in enumerate(questions):
            response = request.POST.get(f'question_{i}', 0)
            responses[question] = int(response)
        
        # Analyze with AI model
        assessment_result = moodigo_ai.analyze_survey(responses)
        
        # Save assessment
        assessment = MentalHealthAssessment.objects.create(
            session=user_session,
            total_score=assessment_result['total_score'],
            risk_level=assessment_result['risk_level'].lower().replace(' ', '_'),
            responses=responses,
            recommendations='; '.join(assessment_result['recommendations'])
        )
        
        return render(request, 'chatbot/assessment_result.html', {
            'assessment': assessment,
            'result': assessment_result
        })

    context = {
        'questions': list(enumerate(questions)),  # Convert to list
        'response_options': [
            (0, 'Never'),
            (1, 'Almost Never'),
            (2, 'Sometimes'),
            (3, 'Fairly Often'),
            (4, 'Very Often')
        ]
    }
    
    return render(request, 'chatbot/assessment.html', context)

def resources(request):
    """Mental health resources page"""
    # Get resources categorized by type
    crisis_resources = Resource.objects.filter(is_crisis=True, is_active=True)
    counseling_resources = Resource.objects.filter(resource_type='counseling', is_active=True)
    app_resources = Resource.objects.filter(resource_type='app', is_active=True)
    article_resources = Resource.objects.filter(resource_type='article', is_active=True)
    
    context = {
        'crisis_resources': crisis_resources,
        'counseling_resources': counseling_resources,
        'app_resources': app_resources,
        'article_resources': article_resources
    }
    
    return render(request, 'chatbot/resources.html', context)

def conversation_history(request):
    """View conversation history"""
    user_session = get_or_create_session(request)
    
    conversations = Conversation.objects.filter(session=user_session)
    paginator = Paginator(conversations, 10)
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'conversations': page_obj
    }
    
    return render(request, 'chatbot/history.html', context)

def view_conversation(request, conversation_id):
    """View specific conversation"""
    user_session = get_or_create_session(request)
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        session=user_session
    )
    
    messages = conversation.messages.all()
    
    context = {
        'conversation': conversation,
        'messages': messages
    }
    
    return render(request, 'chatbot/view_conversation.html', context)

def new_conversation(request):
    """Start a new conversation"""
    user_session = get_or_create_session(request)
    
    # Mark current conversation as inactive
    Conversation.objects.filter(
        session=user_session,
        is_active=True
    ).update(is_active=False)
    
    return redirect('chat')

def crisis_help(request):
    """Crisis support page"""
    crisis_resources = Resource.objects.filter(is_crisis=True, is_active=True)
    
    context = {
        'crisis_resources': crisis_resources
    }
    
    return render(request, 'chatbot/crisis_help.html', context)

@csrf_exempt
def mood_chart_data(request):
    """AJAX endpoint for mood chart data"""
    user_session = get_or_create_session(request)
    
    # Get mood entries from last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    mood_entries = MoodEntry.objects.filter(
        session=user_session,
        created_at__gte=thirty_days_ago
    ).order_by('created_at')
    
    # Prepare data for chart
    chart_data = []
    for entry in mood_entries:
        chart_data.append({
            'date': entry.created_at.strftime('%Y-%m-%d'),
            'mood': entry.mood,
            'intensity': entry.intensity,
            'display_mood': entry.get_mood_display()
        })
    
    return JsonResponse({
        'chart_data': chart_data
    })

def privacy_policy(request):
    """Privacy policy page"""
    return render(request, 'chatbot/privacy.html')

def terms_of_service(request):
    """Terms of service page"""
    return render(request, 'chatbot/terms.html')