from django.core.management.base import BaseCommand
from tasks.scheduled_tasks import setup_scheduled_tasks


class Command(BaseCommand):
    help = 'Setup scheduled tasks for the library system'
    
    def handle(self, *args, **options):
        """Setup all scheduled tasks."""
        try:
            setup_scheduled_tasks()
            self.stdout.write(
                self.style.SUCCESS('Successfully setup scheduled tasks')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up tasks: {str(e)}')
            )