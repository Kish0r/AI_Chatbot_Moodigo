# chatbot/management/commands/export_analytics.py
from django.core.management.base import BaseCommand
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta
from chatbot.models import *
import csv
import json

class Command(BaseCommand):
    help = 'Export analytics data for Moodigo usage analysis'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['csv', 'json'],
            default='csv',
            help='Export format (csv or json)',
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to include in analytics (default: 30)',
        )
    
    def handle(self, *args, **options):
        days = options['days']
        format_type = options['format']
        output_file = options['output']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f'Generating analytics for last {days} days...')
        
        try:
            # Gather analytics data
            analytics_data = self.gather_analytics(cutoff_date)
            
            # Export data
            if format_type == 'csv':
                self.export_csv(analytics_data, output_file)
            else:
                self.export_json(analytics_data, output_file)
            
            self.stdout.write(
                self.style.SUCCESS(f'Analytics exported successfully to {output_file or "stdout"}!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error exporting analytics: {str(e)}')
            )
    
    def gather_analytics(self, cutoff_date):
        """Gather anonymized analytics data"""
        
        # Basic usage statistics
        total_sessions = UserSession.objects.filter(created_at__gte=cutoff_date).count()
        total_conversations = Conversation.objects.filter(created_at__gte=cutoff_date).count()
        total_messages = Message.objects.filter(timestamp__gte=cutoff_date).count()
        
        # User engagement
        avg_messages_per_conversation = Message.objects.filter(
            timestamp__gte=cutoff_date
        ).count() / max(total_conversations, 1)
        
        # Mood tracking
        mood_entries = MoodEntry.objects.filter(created_at__gte=cutoff_date)
        total_mood_entries = mood_entries.count()
        
        if total_mood_entries > 0:
            avg_mood_intensity = mood_entries.aggregate(Avg('intensity'))['intensity__avg']
            mood_distribution = dict(mood_entries.values('mood').annotate(count=Count('mood')).values_list('mood', 'count'))
        else:
            avg_mood_intensity = 0
            mood_distribution = {}
        
        # AI predictions (anonymized)
        ai_predictions = Message.objects.filter(
            timestamp__gte=cutoff_date,
            predicted_condition__isnull=False
        ).values('predicted_condition').annotate(count=Count('predicted_condition'))
        
        prediction_distribution = {pred['predicted_condition']: pred['count'] for pred in ai_predictions}
        
        # Mental health assessments
        assessments = MentalHealthAssessment.objects.filter(created_at__gte=cutoff_date)
        total_assessments = assessments.count()
        
        if total_assessments > 0:
            risk_distribution = dict(assessments.values('risk_level').annotate(count=Count('risk_level')).values_list('risk_level', 'count'))
            avg_assessment_score = assessments.aggregate(Avg('total_score'))['total_score__avg']
        else:
            risk_distribution = {}
            avg_assessment_score = 0
        
        return {
            'period_days': (timezone.now() - cutoff_date).days,
            'generated_at': timezone.now().isoformat(),
            'usage_statistics': {
                'total_sessions': total_sessions,
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'avg_messages_per_conversation': round(avg_messages_per_conversation, 2),
            },
            'mood_tracking': {
                'total_mood_entries': total_mood_entries,
                'avg_mood_intensity': round(avg_mood_intensity or 0, 2),
                'mood_distribution': mood_distribution,
            },
            'ai_predictions': {
                'prediction_distribution': prediction_distribution,
            },
            'assessments': {
                'total_assessments': total_assessments,
                'risk_distribution': risk_distribution,
                'avg_assessment_score': round(avg_assessment_score or 0, 2),
            }
        }
    
    def export_csv(self, data, output_file):
        """Export data as CSV"""
        if output_file:
            with open(output_file, 'w', newline='') as csvfile:
                self._write_csv(csvfile, data)
        else:
            import sys
            self._write_csv(sys.stdout, data)
    
    def _write_csv(self, file, data):
        writer = csv.writer(file)
        
        # Write metadata
        writer.writerow(['Moodigo Analytics Report'])
        writer.writerow(['Generated:', data['generated_at']])
        writer.writerow(['Period:', f"{data['period_days']} days"])
        writer.writerow([])
        
        # Usage statistics
        writer.writerow(['Usage Statistics'])
        for key, value in data['usage_statistics'].items():
            writer.writerow([key.replace('_', ' ').title(), value])
        writer.writerow([])
        
        # Mood tracking
        writer.writerow(['Mood Tracking'])
        writer.writerow(['Total Entries', data['mood_tracking']['total_mood_entries']])
        writer.writerow(['Average Intensity', data['mood_tracking']['avg_mood_intensity']])
        writer.writerow([])
        writer.writerow(['Mood Distribution'])
        for mood, count in data['mood_tracking']['mood_distribution'].items():
            writer.writerow([mood, count])
        writer.writerow([])
        
        # AI Predictions
        writer.writerow(['AI Predictions'])
        for condition, count in data['ai_predictions']['prediction_distribution'].items():
            writer.writerow([condition, count])
        writer.writerow([])
        
        # Assessments
        writer.writerow(['Mental Health Assessments'])
        writer.writerow(['Total Assessments', data['assessments']['total_assessments']])
        writer.writerow(['Average Score', data['assessments']['avg_assessment_score']])
        writer.writerow([])
        writer.writerow(['Risk Distribution'])
        for risk, count in data['assessments']['risk_distribution'].items():
            writer.writerow([risk, count])
    
    def export_json(self, data, output_file):
        """Export data as JSON"""
        if output_file:
            with open(output_file, 'w') as jsonfile:
                json.dump(data, jsonfile, indent=2, default=str)
        else:
            self.stdout.write(json.dumps(data, indent=2, default=str))