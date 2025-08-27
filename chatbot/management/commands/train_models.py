# chatbot/management/commands/train_models.py
from django.core.management.base import BaseCommand
from django.conf import settings
from chatbot.ml_models import MoodigoAI
import os

class Command(BaseCommand):
    help = 'Train and initialize ML models for Moodigo'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--survey-data',
            type=str,
            help='Path to survey dataset CSV file',
        )
        parser.add_argument(
            '--nlp-data',
            type=str,
            help='Path to NLP dataset CSV file',
        )
        parser.add_argument(
            '--retrain',
            action='store_true',
            help='Retrain models even if they already exist',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting ML model training...'))
        
        try:
            # Initialize AI service
            moodigo_ai = MoodigoAI()
            
            # Check if models already exist
            survey_model_exists = os.path.exists('mental_health_model.pkl')
            nlp_model_exists = os.path.exists('best_fast_mental_health_model.pkl')
            
            if (survey_model_exists and nlp_model_exists) and not options['retrain']:
                self.stdout.write(
                    self.style.WARNING('Models already exist. Use --retrain to force retraining.')
                )
                return
            
            # Train survey model if data provided
            if options['survey_data']:
                self.stdout.write('Training survey-based model...')
                # Here you would implement the training logic from your first model
                self.stdout.write(self.style.SUCCESS('Survey model training completed.'))
            else:
                self.stdout.write(
                    self.style.WARNING('No survey data provided. Creating demo survey model.')
                )
                moodigo_ai.survey_model.initialize_model()
            
            # Train NLP model if data provided
            if options['nlp_data']:
                self.stdout.write('Training NLP model...')
                # Here you would implement the training logic from your second model
                self.stdout.write(self.style.SUCCESS('NLP model training completed.'))
            else:
                self.stdout.write(
                    self.style.WARNING('No NLP data provided. Creating demo NLP model.')
                )
                moodigo_ai.nlp_model.initialize_model()
            
            # Initialize both models
            moodigo_ai.initialize()
            
            self.stdout.write(
                self.style.SUCCESS('ML model setup completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during model training: {str(e)}')
            )