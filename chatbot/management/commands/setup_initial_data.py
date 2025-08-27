# chatbot/management/commands/setup_initial_data.py
from django.core.management.base import BaseCommand
from django.db import transaction
from chatbot.models import Resource
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Set up initial data for Moodigo including mental health resources'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing resources',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up initial data for Moodigo...'))
        
        try:
            with transaction.atomic():
                self.create_crisis_resources(options['force'])
                self.create_counseling_resources(options['force'])
                self.create_app_resources(options['force'])
                self.create_article_resources(options['force'])
                
            self.stdout.write(
                self.style.SUCCESS('Successfully set up initial data!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up initial data: {str(e)}')
            )
    
    def create_crisis_resources(self, force=False):
        """Create crisis support resources"""
        crisis_resources = [
            {
                'title': '988 Suicide & Crisis Lifeline',
                'description': 'Free and confidential emotional support 24/7 for people in suicidal crisis or emotional distress. Available nationwide in the United States.',
                'resource_type': 'crisis',
                'phone_number': '988',
                'url': 'https://988lifeline.org/',
                'is_crisis': True,
            },
            {
                'title': 'Crisis Text Line',
                'description': 'Free crisis counseling via text message. Trained volunteers provide support for anyone in crisis, connecting them with resources.',
                'resource_type': 'crisis',
                'phone_number': '741741',
                'url': 'https://www.crisistextline.org/',
                'is_crisis': True,
            },
            {
                'title': 'SAMHSA National Helpline',
                'description': 'Free treatment referral and information service for individuals facing mental health and/or substance use disorders.',
                'resource_type': 'crisis',
                'phone_number': '1-800-662-4357',
                'url': 'https://www.samhsa.gov/find-help/national-helpline',
                'is_crisis': True,
            },
            {
                'title': 'The Trevor Project',
                'description': 'Crisis intervention and suicide prevention services for LGBTQ+ young people under 25.',
                'resource_type': 'crisis',
                'phone_number': '1-866-488-7386',
                'url': 'https://www.thetrevorproject.org/',
                'is_crisis': True,
            },
            {
                'title': 'National Domestic Violence Hotline',
                'description': '24/7 confidential support for domestic violence survivors and their loved ones.',
                'resource_type': 'crisis',
                'phone_number': '1-800-799-7233',
                'url': 'https://www.thehotline.org/',
                'is_crisis': True,
            },
        ]
        
        for resource_data in crisis_resources:
            resource, created = Resource.objects.get_or_create(
                title=resource_data['title'],
                defaults=resource_data
            )
            if not created and force:
                for key, value in resource_data.items():
                    setattr(resource, key, value)
                resource.save()
                self.stdout.write(f'Updated crisis resource: {resource.title}')
            elif created:
                self.stdout.write(f'Created crisis resource: {resource.title}')
    
    def create_counseling_resources(self, force=False):
        """Create counseling and therapy resources"""
        counseling_resources = [
            {
                'title': 'Psychology Today',
                'description': 'Find therapists, psychiatrists, and mental health professionals in your area. Comprehensive directory with filters for insurance, specialties, and more.',
                'resource_type': 'counseling',
                'url': 'https://www.psychologytoday.com/us/therapists',
            },
            {
                'title': 'BetterHelp',
                'description': 'Online therapy platform with licensed, trained, and experienced therapists. Accessible from anywhere with internet connection.',
                'resource_type': 'counseling',
                'url': 'https://www.betterhelp.com/',
            },
            {
                'title': 'Talkspace',
                'description': 'Online therapy and counseling services with licensed therapists. Text, audio, and video sessions available.',
                'resource_type': 'counseling',
                'url': 'https://www.talkspace.com/',
            },
            {
                'title': 'NAMI (National Alliance on Mental Illness)',
                'description': 'Local NAMI chapters provide support groups, education programs, and advocacy. Find your local chapter for in-person resources.',
                'resource_type': 'counseling',
                'url': 'https://www.nami.org/',
            },
            {
                'title': 'Open Path Psychotherapy Collective',
                'description': 'Affordable therapy options with sessions ranging from $30-$60. Non-profit organization helping make therapy accessible.',
                'resource_type': 'counseling',
                'url': 'https://openpathcollective.org/',
            },
        ]
        
        for resource_data in counseling_resources:
            resource, created = Resource.objects.get_or_create(
                title=resource_data['title'],
                defaults=resource_data
            )
            if not created and force:
                for key, value in resource_data.items():
                    setattr(resource, key, value)
                resource.save()
                self.stdout.write(f'Updated counseling resource: {resource.title}')
            elif created:
                self.stdout.write(f'Created counseling resource: {resource.title}')
    
    def create_app_resources(self, force=False):
        """Create mental health app resources"""
        app_resources = [
            {
                'title': 'Headspace',
                'description': 'Meditation and mindfulness app with guided sessions for anxiety, stress, sleep, and focus. Beginner-friendly with progress tracking.',
                'resource_type': 'app',
                'url': 'https://www.headspace.com/',
            },
            {
                'title': 'Calm',
                'description': 'Sleep stories, meditation, and relaxation techniques. Features nature sounds, breathing programs, and masterclasses on mindfulness.',
                'resource_type': 'app',
                'url': 'https://www.calm.com/',
            },
            {
                'title': 'Sanvello',
                'description': 'Anxiety and depression support with mood tracking, guided journeys, and coping tools based on cognitive behavioral therapy.',
                'resource_type': 'app',
                'url': 'https://www.sanvello.com/',
            },
            {
                'title': 'Youper',
                'description': 'AI-powered emotional health assistant that helps track moods and provides personalized conversations for better mental health.',
                'resource_type': 'app',
                'url': 'https://www.youper.ai/',
            },
            {
                'title': 'Talklife',
                'description': 'Peer support network where people share experiences and support each other through difficult times. Moderated community.',
                'resource_type': 'app',
                'url': 'https://www.talklife.co/',
            },
            {
                'title': 'MindShift',
                'description': 'Free app to help teens and young adults cope with anxiety. Based on cognitive behavioral therapy principles.',
                'resource_type': 'app',
                'url': 'https://www.anxietycanada.com/resources/mindshift-app/',
            },
            {
                'title': 'PTSD Coach',
                'description': 'Evidence-based app for managing PTSD symptoms. Created by the US Department of Veterans Affairs.',
                'resource_type': 'app',
                'url': 'https://www.ptsd.va.gov/appvid/mobile/',
            },
        ]
        
        for resource_data in app_resources:
            resource, created = Resource.objects.get_or_create(
                title=resource_data['title'],
                defaults=resource_data
            )
            if not created and force:
                for key, value in resource_data.items():
                    setattr(resource, key, value)
                resource.save()
                self.stdout.write(f'Updated app resource: {resource.title}')
            elif created:
                self.stdout.write(f'Created app resource: {resource.title}')
    
    def create_article_resources(self, force=False):
        """Create educational article and guide resources"""
        article_resources = [
            {
                'title': 'Mental Health America',
                'description': 'Comprehensive resources on mental health conditions, screening tools, and advocacy. Evidence-based information and support.',
                'resource_type': 'article',
                'url': 'https://www.mhanational.org/',
            },
            {
                'title': 'National Institute of Mental Health (NIMH)',
                'description': 'Research-based information on mental health disorders, treatments, and ongoing studies. Government resource with latest scientific findings.',
                'resource_type': 'article',
                'url': 'https://www.nimh.nih.gov/',
            },
            {
                'title': 'Mayo Clinic Mental Health',
                'description': 'Medical information on mental health conditions, symptoms, causes, and treatments from trusted healthcare professionals.',
                'resource_type': 'article',
                'url': 'https://www.mayoclinic.org/diseases-conditions/mental-illness/symptoms-causes/syc-20374968',
            },
            {
                'title': 'American Psychological Association (APA)',
                'description': 'Professional resources on psychology, mental health research, and evidence-based treatment approaches.',
                'resource_type': 'article',
                'url': 'https://www.apa.org/topics/mental-health',
            },
            {
                'title': 'Centre for Addiction and Mental Health (CAMH)',
                'description': 'Educational resources on mental health and addiction, including self-help tools and family support information.',
                'resource_type': 'article',
                'url': 'https://www.camh.ca/',
            },
            {
                'title': 'Mindfulness-Based Stress Reduction',
                'description': 'Learn about MBSR techniques for managing stress, anxiety, and depression. Includes guided exercises and research.',
                'resource_type': 'article',
                'url': 'https://www.mindfulnessmbbsr.com/',
            },
        ]
        
        for resource_data in article_resources:
            resource, created = Resource.objects.get_or_create(
                title=resource_data['title'],
                defaults=resource_data
            )
            if not created and force:
                for key, value in resource_data.items():
                    setattr(resource, key, value)
                resource.save()
                self.stdout.write(f'Updated article resource: {resource.title}')
            elif created:
                self.stdout.write(f'Created article resource: {resource.title}')