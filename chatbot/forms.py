# chatbot/forms.py
from django import forms
from .models import MoodEntry, MentalHealthAssessment

class MoodEntryForm(forms.ModelForm):
    class Meta:
        model = MoodEntry
        fields = ['mood', 'intensity', 'notes']
        widgets = {
            'mood': forms.Select(attrs={
                'class': 'form-select form-select-lg mb-3',
                'style': 'font-size: 1.2rem; padding: 0.75rem;'
            }),
            'intensity': forms.Select(attrs={
                'class': 'form-select form-select-lg mb-3',
                'style': 'font-size: 1.2rem; padding: 0.75rem;'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'How are you feeling today? (optional)',
                'style': 'resize: vertical;'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notes'].required = False
        
        # Add custom labels
        self.fields['mood'].label = "How are you feeling?"
        self.fields['intensity'].label = "How intense is this feeling? (1 = Very Low, 10 = Very High)"
        self.fields['notes'].label = "Additional notes"

class SurveyForm(forms.Form):
    """Mental health assessment survey form"""
    
    RESPONSE_CHOICES = [
        (0, 'Never'),
        (1, 'Almost Never'),
        (2, 'Sometimes'),
        (3, 'Fairly Often'),
        (4, 'Very Often')
    ]
    
    def __init__(self, questions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for i, question in enumerate(questions):
            field_name = f'question_{i}'
            self.fields[field_name] = forms.ChoiceField(
                label=question,
                choices=self.RESPONSE_CHOICES,
                widget=forms.RadioSelect(attrs={
                    'class': 'form-check-input'
                }),
                initial=0
            )

class ContactForm(forms.Form):
    """Contact form for user inquiries"""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        })
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Your message...'
        })
    )
    
    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message) < 10:
            raise forms.ValidationError("Message must be at least 10 characters long.")
        return message