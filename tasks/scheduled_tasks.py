from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Q, Sum, Count
from django_q.tasks import schedule
from django_q.models import Schedule
from borrowings.models import Borrowing
from payments.models import Payment
from notifications.signals import check_overdue_books, send_daily_summary
from payments.fine_service import FineCalculationService
from notifications.services import TelegramNotificationService


def setup_scheduled_tasks():
    """Setup all scheduled tasks for the library system."""
    
    # Daily summary at 9:00 AM
    schedule(
        'tasks.scheduled_tasks.send_daily_summary_task',
        schedule_type=Schedule.DAILY,
        next_run=timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
    )
    
    # Check overdue books daily at 8:00 AM
    schedule(
        'tasks.scheduled_tasks.check_overdue_books_task',
        schedule_type=Schedule.DAILY,
        next_run=timezone.now().replace(hour=8, minute=0, second=0, microsecond=0)
    )
    
    # Process fines daily at 8:30 AM
    schedule(
        'tasks.scheduled_tasks.process_fines_task',
        schedule_type=Schedule.DAILY,
        next_run=timezone.now().replace(hour=8, minute=30, second=0, microsecond=0)
    )
    
    # Weekly statistics every Monday at 10:00 AM
    schedule(
        'tasks.scheduled_tasks.send_weekly_summary_task',
        schedule_type=Schedule.WEEKLY,
        next_run=timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
    )
    
    # Monthly report on 1st of month at 11:00 AM
    schedule(
        'tasks.scheduled_tasks.send_monthly_report_task',
        schedule_type=Schedule.MONTHLY,
        next_run=timezone.now().replace(hour=11, minute=0, second=0, microsecond=0)
    )


def send_daily_summary_task():
    """Send daily summary notification."""
    try:
        send_daily_summary()
        print("Daily summary sent successfully")
    except Exception as e:
        print(f"Error sending daily summary: {str(e)}")


def check_overdue_books_task():
    """Check for overdue books and send notifications."""
    try:
        check_overdue_books()
        print("Overdue books check completed")
    except Exception as e:
        print(f"Error checking overdue books: {str(e)}")


def process_fines_task():
    """Process overdue books and create fines."""
    try:
        fine_service = FineCalculationService()
        result = fine_service.process_overdue_books()
        print(f"Fine processing completed: {result}")
    except Exception as e:
        print(f"Error processing fines: {str(e)}")


def send_weekly_summary_task():
    """Send weekly summary notification."""
    try:
        today = date.today()
        week_ago = today - timedelta(days=7)
        
        # Get weekly statistics
        new_borrowings = Borrowing.objects.filter(
            borrow_date__gte=week_ago,
            borrow_date__lte=today
        ).count()
        
        returns = Borrowing.objects.filter(
            actual_return_date__gte=week_ago,
            actual_return_date__lte=today
        ).count()
        
        payments = Payment.objects.filter(
            status='PAID',
            borrowing__borrow_date__gte=week_ago,
            borrowing__borrow_date__lte=today
        ).count()
        
        revenue = sum(
            payment.money_to_pay for payment in Payment.objects.filter(
                status='PAID',
                borrowing__borrow_date__gte=week_ago,
                borrowing__borrow_date__lte=today
            )
        )
        
        overdue = Borrowing.objects.filter(
            expected_return_date__lt=today,
            actual_return_date__isnull=True
        ).count()
        
        # Send weekly summary
        telegram_service = TelegramNotificationService()
        message = (
            f"📊 <b>Weekly Library Summary</b>\n\n"
            f"📅 Period: {week_ago} to {today}\n\n"
            f"📚 New Borrowings: {new_borrowings}\n"
            f"📖 Returns: {returns}\n"
            f"💳 Payments: {payments}\n"
            f"⚠️ Overdue Books: {overdue}\n"
            f"💰 Revenue: ${revenue}\n\n"
            f"📈 Weekly Performance Report"
        )
        
        telegram_service.send_message(message)
        print("Weekly summary sent successfully")
        
    except Exception as e:
        print(f"Error sending weekly summary: {str(e)}")


def send_monthly_report_task():
    """Send monthly report notification."""
    try:
        today = date.today()
        month_ago = today - timedelta(days=30)
        
        # Get monthly statistics
        new_borrowings = Borrowing.objects.filter(
            borrow_date__gte=month_ago,
            borrow_date__lte=today
        ).count()
        
        returns = Borrowing.objects.filter(
            actual_return_date__gte=month_ago,
            actual_return_date__lte=today
        ).count()
        
        payments = Payment.objects.filter(
            status='PAID',
            borrowing__borrow_date__gte=month_ago,
            borrowing__borrow_date__lte=today
        ).count()
        
        revenue = sum(
            payment.money_to_pay for payment in Payment.objects.filter(
                status='PAID',
                borrowing__borrow_date__gte=month_ago,
                borrowing__borrow_date__lte=today
            )
        )
        
        fine_revenue = sum(
            payment.money_to_pay for payment in Payment.objects.filter(
                type='FINE',
                status='PAID',
                borrowing__borrow_date__gte=month_ago,
                borrowing__borrow_date__lte=today
            )
        )
        
        overdue = Borrowing.objects.filter(
            expected_return_date__lt=today,
            actual_return_date__isnull=True
        ).count()
        
        # Get top books
        top_books = Borrowing.objects.filter(
            borrow_date__gte=month_ago
        ).values('book__title').annotate(
            borrow_count=Count('id')
        ).order_by('-borrow_count')[:5]
        
        # Send monthly report
        telegram_service = TelegramNotificationService()
        message = (
            f"📊 <b>Monthly Library Report</b>\n\n"
            f"📅 Period: {month_ago} to {today}\n\n"
            f"📚 New Borrowings: {new_borrowings}\n"
            f"📖 Returns: {returns}\n"
            f"💳 Payments: {payments}\n"
            f"⚠️ Overdue Books: {overdue}\n"
            f"💰 Total Revenue: ${revenue}\n"
            f"💰 Fine Revenue: ${fine_revenue}\n\n"
            f"📈 Top Books This Month:\n"
        )
        
        for i, book in enumerate(top_books, 1):
            message += f"{i}. {book['book__title']} ({book['borrow_count']} times)\n"
        
        telegram_service.send_message(message)
        print("Monthly report sent successfully")
        
    except Exception as e:
        print(f"Error sending monthly report: {str(e)}")


def cleanup_expired_payments_task():
    """Clean up expired payment sessions."""
    try:
        from datetime import datetime, timedelta
        
        # Find payments that are older than 24 hours and still pending
        yesterday = timezone.now() - timedelta(hours=24)
        expired_payments = Payment.objects.filter(
            status='PENDING',
            borrowing__borrow_date__lt=yesterday
        )
        
        expired_count = expired_payments.count()
        expired_payments.update(status='EXPIRED')
        
        if expired_count > 0:
            print(f"Cleaned up {expired_count} expired payments")
            
            # Send notification about cleanup
            telegram_service = TelegramNotificationService()
            telegram_service.send_message(
                f"🧹 <b>Payment Cleanup</b>\n\n"
                f"Cleaned up {expired_count} expired payment sessions\n"
                f"Timestamp: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        
    except Exception as e:
        print(f"Error cleaning up expired payments: {str(e)}")


def send_reminder_notifications_task():
    """Send reminder notifications for books due soon."""
    try:
        today = date.today()
        tomorrow = today + timedelta(days=1)
        day_after_tomorrow = today + timedelta(days=2)
        
        # Find borrowings due in next 2 days
        due_soon = Borrowing.objects.filter(
            expected_return_date__in=[tomorrow, day_after_tomorrow],
            actual_return_date__isnull=True
        ).select_related('user', 'book')
        
        telegram_service = TelegramNotificationService()
        
        for borrowing in due_soon:
            days_until_due = (borrowing.expected_return_date - today).days
            
            message = (
                f"📚 <b>Return Reminder</b>\n\n"
                f"👤 User: {borrowing.user.get_full_name() or borrowing.user.email}\n"
                f"📖 Book: {borrowing.book.title} by {borrowing.book.author}\n"
                f"📅 Due Date: {borrowing.expected_return_date}\n"
                f"⏰ Days Until Due: {days_until_due}\n\n"
                f"Please return the book on time to avoid fines.\n\n"
                f"ID: {borrowing.id}"
            )
            
            telegram_service.send_message(message)
        
        if due_soon.count() > 0:
            print(f"Sent {due_soon.count()} reminder notifications")
        
    except Exception as e:
        print(f"Error sending reminder notifications: {str(e)}")


def generate_system_health_report():
    """Generate and send system health report."""
    try:
        today = date.today()
        
        # System statistics
        total_books = Borrowing.objects.count()
        active_borrowings = Borrowing.objects.filter(
            actual_return_date__isnull=True
        ).count()
        
        overdue_books = Borrowing.objects.filter(
            expected_return_date__lt=today,
            actual_return_date__isnull=True
        ).count()
        
        pending_payments = Payment.objects.filter(status='PENDING').count()
        paid_payments = Payment.objects.filter(status='PAID').count()
        
        # Calculate success rate
        total_payments = Payment.objects.count()
        success_rate = (paid_payments / total_payments * 100) if total_payments > 0 else 0
        
        message = (
            f"🏥 <b>System Health Report</b>\n\n"
            f"📊 Statistics:\n"
            f"📚 Total Borrowings: {total_books}\n"
            f"📖 Active Borrowings: {active_borrowings}\n"
            f"⚠️ Overdue Books: {overdue_books}\n"
            f"💳 Pending Payments: {pending_payments}\n"
            f"✅ Paid Payments: {paid_payments}\n"
            f"📈 Payment Success Rate: {success_rate:.1f}%\n\n"
            f"🕐 Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        telegram_service = TelegramNotificationService()
        telegram_service.send_message(message)
        print("System health report sent successfully")
        
    except Exception as e:
        print(f"Error generating system health report: {str(e)}")