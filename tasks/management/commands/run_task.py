from django.core.management.base import BaseCommand
from tasks.scheduled_tasks import (
    send_daily_summary_task,
    check_overdue_books_task,
    process_fines_task,
    send_weekly_summary_task,
    send_monthly_report_task,
    cleanup_expired_payments_task,
    send_reminder_notifications_task,
    generate_system_health_report
)


class Command(BaseCommand):
    help = 'Run a specific scheduled task'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'task_name',
            type=str,
            help='Name of the task to run'
        )
    
    def handle(self, *args, **options):
        """Run the specified task."""
        task_name = options['task_name']
        
        # Task mapping
        tasks = {
            'daily_summary': send_daily_summary_task,
            'overdue_check': check_overdue_books_task,
            'process_fines': process_fines_task,
            'weekly_summary': send_weekly_summary_task,
            'monthly_report': send_monthly_report_task,
            'cleanup_payments': cleanup_expired_payments_task,
            'reminder_notifications': send_reminder_notifications_task,
            'system_health': generate_system_health_report,
        }
        
        if task_name not in tasks:
            self.stdout.write(
                self.style.ERROR(f'Unknown task: {task_name}')
            )
            self.stdout.write(
                self.style.WARNING('Available tasks: ' + ', '.join(tasks.keys()))
            )
            return
        
        try:
            task_func = tasks[task_name]
            task_func()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully ran task: {task_name}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error running task {task_name}: {str(e)}')
            )