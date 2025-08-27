# chatbot/ml_models.py
import pandas as pd
import numpy as np
import pickle
import re
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from collections import Counter
import warnings

warnings.filterwarnings('ignore')

class MentalHealthPredictor:
    """Survey-based mental health risk prediction"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_name = None
        self.accuracy = 0
        self.mental_health_questions = []
        
    def initialize_model(self):
        """Initialize with pre-trained model or create new one"""
        try:
            # Try to load existing model
            with open('mental_health_model.pkl', 'rb') as f:
                model_package = pickle.load(f)
                self.model = model_package['model']
                self.scaler = model_package.get('scaler')
                self.model_name = model_package['model_name']
                self.accuracy = model_package['accuracy']
            print(f"Loaded existing model: {self.model_name}")
        except FileNotFoundError:
            # Create a basic model if file doesn't exist
            self._create_basic_model()
    
    def _create_basic_model(self):
        """Create a basic model for demonstration"""
        print("Creating basic model for demonstration...")
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model_name = "Random Forest (Demo)"
        self.accuracy = 0.85
        
        # Create dummy mental health questions
        self.mental_health_questions = [
            "Feeling nervous or anxious",
            "Not being able to stop worrying",
            "Feeling down or depressed",
            "Little interest in doing things",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself",
            "Trouble concentrating",
            "Moving or speaking slowly",
            "Thoughts of self-harm"
        ]
        
        # Train with dummy data for demo purposes
        X_dummy = np.random.randint(0, 5, (100, len(self.mental_health_questions)))
        y_dummy = np.random.choice(['Low Risk', 'Moderate Risk', 'High Risk', 'Very High Risk'], 100)
        self.model.fit(X_dummy, y_dummy)
    
    def predict_risk(self, responses):
        """Predict mental health risk based on survey responses"""
        if self.model is None:
            self.initialize_model()
        
        # Convert responses to proper format
        if isinstance(responses, dict):
            # Convert dictionary responses to array
            response_array = [responses.get(q, 0) for q in self.mental_health_questions]
        else:
            response_array = responses
        
        # Ensure we have the right number of features
        if len(response_array) != len(self.mental_health_questions):
            response_array = response_array[:len(self.mental_health_questions)]
            response_array.extend([0] * (len(self.mental_health_questions) - len(response_array)))
        
        # Make prediction
        response_df = pd.DataFrame([response_array], columns=self.mental_health_questions)
        prediction = self.model.predict(response_df)[0]
        probabilities = self.model.predict_proba(response_df)[0]
        
        # Calculate confidence
        max_prob = max(probabilities)
        
        return {
            'risk_level': prediction,
            'confidence': float(max_prob),
            'total_score': sum(response_array),
            'recommendations': self._get_recommendations(prediction)
        }
    
    def _get_recommendations(self, risk_level):
        """Get recommendations based on risk level"""
        recommendations = {
            'Low Risk': [
                "Continue maintaining healthy habits",
                "Regular exercise and good sleep schedule",
                "Stay connected with friends and family"
            ],
            'Moderate Risk': [
                "Consider speaking with a counselor",
                "Practice stress management techniques",
                "Monitor your mental health regularly"
            ],
            'High Risk': [
                "Strongly recommend professional counseling",
                "Reach out to mental health services",
                "Consider therapy or support groups"
            ],
            'Very High Risk': [
                "Seek immediate professional help",
                "Contact crisis support services",
                "Reach out to trusted friends or family"
            ]
        }
        return recommendations.get(risk_level, [])

class NLPMentalHealthAnalyzer:
    """NLP-based mental health analysis from text"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.categories = ['Normal', 'Depression', 'Suicidal', 'Anxiety', 'Bipolar', 'Stress', 'Personality disorder']
        self.best_model_type = 'tfidf'
        
        # Mental health keywords
        self.mental_health_patterns = {
            'depression_words': ['depressed', 'sad', 'hopeless', 'worthless', 'empty', 'crying', 'grief'],
            'anxiety_words': ['anxious', 'worried', 'panic', 'nervous', 'fear', 'restless', 'tension'],
            'suicidal_words': ['suicide', 'kill', 'death', 'die', 'end', 'hurt myself', 'done with life'],
            'stress_words': ['stressed', 'overwhelmed', 'pressure', 'burden', 'exhausted', 'breaking'],
            'bipolar_words': ['manic', 'mood swing', 'high energy', 'low energy', 'impulsive', 'racing'],
            'personality_words': ['unstable', 'intense', 'abandonment', 'identity', 'emptiness', 'anger'],
            'positive_words': ['happy', 'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic'],
            'intensity_words': ['very', 'extremely', 'really', 'so', 'too', 'completely', 'totally']
        }
        
        self.stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'
        }
        
    def initialize_model(self):
        """Initialize the NLP model"""
        try:
            # Try to load existing model
            with open('best_fast_mental_health_model.pkl', 'rb') as f:
                model_package = pickle.load(f)
                self.model = model_package['model']
                self.vectorizer = model_package['vectorizer']
                self.best_model_type = model_package.get('best_model_type', 'tfidf')
            print("Loaded existing NLP model")
        except FileNotFoundError:
            self._create_basic_nlp_model()
    
    def _create_basic_nlp_model(self):
        """Create a basic NLP model for demonstration"""
        print("Creating basic NLP model for demonstration...")
        self.model = LogisticRegression(random_state=42, max_iter=1000)
        self.vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        
        # Create dummy training data
        dummy_texts = [
            "I feel really anxious about my exams",
            "I'm so depressed and nothing matters",
            "Life is great and I'm feeling amazing",
            "I'm stressed about work and studies",
            "Sometimes I think about ending it all",
            "My mood keeps changing rapidly",
            "I feel empty and don't know who I am"
        ]
        
        dummy_labels = ['Anxiety', 'Depression', 'Normal', 'Stress', 'Suicidal', 'Bipolar', 'Personality disorder']
        
        # Train the model
        X_dummy = self.vectorizer.fit_transform(dummy_texts)
        self.model.fit(X_dummy, dummy_labels)
    
    def preprocess_text(self, text):
        """Preprocess text for analysis"""
        if pd.isna(text):
            return ""
        
        text = str(text).lower()
        text = re.sub(r"can't|cannot", "cannot", text)
        text = re.sub(r"won't|will not", "will not", text)
        text = re.sub(r"n't", " not", text)
        text = re.sub(r'http\S+|www\S+|@\w+|#\w+', '', text)
        text = re.sub(r'[^\w\s!?.,]', ' ', text)
        text = re.sub(r'([!?])\1+', r'\1\1', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def analyze_text(self, text):
        """Analyze text and predict mental health condition"""
        if self.model is None:
            self.initialize_model()
        
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        if not processed_text:
            return None, {}, 0.0
        
        try:
            # Transform text using vectorizer
            text_features = self.vectorizer.transform([processed_text])
            
            # Make prediction
            prediction = self.model.predict(text_features)[0]
            probabilities = self.model.predict_proba(text_features)[0]
            
            # Create probability dictionary
            prob_dict = {}
            for i, class_name in enumerate(self.model.classes_):
                prob_dict[class_name] = float(probabilities[i])
            
            confidence = max(probabilities)
            
            return prediction, prob_dict, float(confidence)
            
        except Exception as e:
            print(f"Error in text analysis: {e}")
            return "Normal", {"Normal": 1.0}, 1.0

class MoodigoAI:
    """Main AI service that combines both models"""
    
    def __init__(self):
        self.survey_model = MentalHealthPredictor()
        self.nlp_model = NLPMentalHealthAnalyzer()
        self.conversation_context = []
        
    def initialize(self):
        """Initialize both models"""
        self.survey_model.initialize_model()
        self.nlp_model.initialize_model()
        
    def analyze_message(self, message):
        """Analyze user message using NLP model"""
        prediction, probabilities, confidence = self.nlp_model.analyze_text(message)
        
        return {
            'prediction': prediction,
            'probabilities': probabilities,
            'confidence': confidence,
            'response': self._generate_response(prediction, confidence)
        }
    
    def analyze_survey(self, responses):
        """Analyze survey responses"""
        return self.survey_model.predict_risk(responses)
    
    def _generate_response(self, prediction, confidence):
        """Generate appropriate response based on prediction"""
        responses = {
            'Normal': {
                'high': "That's wonderful! You seem to be in a positive mental space. Keep up the great work! 😊",
                'medium': "It sounds like you're doing okay overall. That's good to hear! 😊",
                'low': "I'm getting some positive signals. How are you feeling overall?"
            },
            'Anxiety': {
                'high': "I can sense significant anxiety in your message. Try the 4-7-8 breathing technique: breathe in for 4, hold for 7, exhale for 8. 💙",
                'medium': "You seem anxious about something. Deep breathing and grounding exercises can help. 💙",
                'low': "I'm detecting some possible anxiety. Is there something specific worrying you?"
            },
            'Depression': {
                'high': "I'm very concerned about what you're sharing. These feelings are serious but treatable. Please consider reaching out to a mental health professional. 💜",
                'medium': "It sounds like you're going through a difficult time. You're not alone in this. 💜",
                'low': "I'm sensing some challenging emotions. How long have you been feeling this way?"
            },
            'Stress': {
                'high': "You seem to be under significant stress. Try to identify the main stressor and take breaks when possible. 💚",
                'medium': "Stress can be overwhelming. What's your biggest source of stress right now? 💚",
                'low': "I'm picking up on some possible stress. Are you feeling overwhelmed about anything?"
            },
            'Suicidal': {
                'high': "I'm extremely concerned about you. Please reach out for immediate help: 988 (US) or contact emergency services. Your life has value. 🆘",
                'medium': "I'm worried about you. Please talk to someone you trust or a crisis counselor: 988. 🆘",
                'low': "Some of your words concern me. Are you having thoughts of hurting yourself?"
            },
            'Bipolar': {
                'high': "The mood patterns you're describing suggest you should speak with a mental health professional about bipolar disorder. 🏥",
                'medium': "Your mood changes might benefit from professional evaluation. Are you seeing a doctor? 🏥",
                'low': "I'm noticing some mood-related patterns. How have your energy levels been?"
            },
            'Personality disorder': {
                'high': "The relationship and identity patterns you mention could benefit from specialized therapy. DBT can be particularly helpful. 🤝",
                'medium': "These interpersonal patterns might be worth exploring with a therapist. 🤝",
                'low': "I'm noticing some relationship-related concerns. How are your relationships feeling lately?"
            }
        }
        
        # Determine confidence level
        if confidence >= 0.7:
            level = 'high'
        elif confidence >= 0.5:
            level = 'medium'
        else:
            level = 'low'
        
        response = responses.get(prediction, {}).get(level, "I'm here to listen. How can I help you today?")
        
        # Add crisis resources for high-risk situations
        if prediction == 'Suicidal' or (prediction == 'Depression' and confidence > 0.8):
            response += "\n\n🔗 Additional resources:\n• National Suicide Prevention Lifeline: 988\n• Crisis Text Line: Text HOME to 741741"
        
        return response
    
    def get_mood_insights(self, mood_history):
        """Analyze mood patterns over time"""
        if not mood_history:
            return "Not enough data for mood insights."
        
        # Analyze mood trends
        moods = [entry.mood for entry in list(mood_history)[:7]]
        # Last 7 entries
        mood_counts = Counter(moods)
        most_common_mood = mood_counts.most_common(1)[0][0]
        
        insights = f"Your most frequent mood this week has been {most_common_mood.replace('_', ' ')}. "
        
        # Add recommendations based on patterns
        if 'sad' in most_common_mood or 'stressed' in most_common_mood:
            insights += "Consider practicing mindfulness or reaching out for support."
        elif 'happy' in most_common_mood:
            insights += "Great to see you're feeling positive! Keep up the good habits."
        else:
            insights += "Your moods seem balanced. Continue monitoring your emotional well-being."
        
        return insights