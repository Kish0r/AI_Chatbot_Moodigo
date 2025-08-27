# chatbot/management/commands/cleanup_old_sessions.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from chatbot.models import UserSession, Conversation, Message, MoodEntry
from django.db import transaction

class Command(BaseCommand):
    help = 'Clean up old anonymous user sessions and associated data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete sessions older than this many days (default: 30)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
    
    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(
            f'Finding sessions older than {days} days (before {cutoff_date.date()})...'
        )
        
        # Find old anonymous sessions
        old_sessions = UserSession.objects.filter(
            is_anonymous=True,
            last_activity__lt=cutoff_date
        )
        
        session_count = old_sessions.count()
        
        if session_count == 0:
            self.stdout.write(self.style.SUCCESS('No old sessions found to cleanup.'))
            return
        
        # Count related objects
        conversation_count = Conversation.objects.filter(session__in=old_sessions).count()
        message_count = Message.objects.filter(conversation__session__in=old_sessions).count()
        mood_entry_count = MoodEntry.objects.filter(session__in=old_sessions).count()
        
        self.stdout.write(f'Found for cleanup:')
        self.stdout.write(f'  - {session_count} old sessions')
        self.stdout.write(f'  - {conversation_count} conversations')
        self.stdout.write(f'  - {message_count} messages')
        self.stdout.write(f'  - {mood_entry_count} mood entries')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN: No data was actually deleted.')
            )
            return
        
        # Confirm deletion
        confirm = input('Are you sure you want to delete this data? (yes/no): ')
        if confirm.lower() != 'yes':
            self.stdout.write('Cleanup cancelled.')
            return
        
        try:
            with transaction.atomic():
                # Delete will cascade to related objects
                deleted_count = old_sessions.delete()[0]
                
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {deleted_count} old sessions and related data.')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during cleanup: {str(e)}')
            )