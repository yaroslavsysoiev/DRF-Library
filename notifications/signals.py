from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import date
from borrowings.models import Borrowing
from payments.models import Payment
from .services import TelegramNotificationService


@receiver(post_save, sender=Borrowing)
def send_borrowing_notification(sender, instance, created, **kwargs):
    """
    Send Telegram notification when a new borrowing is created.
    """
    if created:
        try:
            telegram_service = TelegramNotificationService()
            telegram_service.send_borrowing_notification(instance)
        except Exception as e:
            # Log error but don't break the borrowing creation
            print(f"Failed to send borrowing notification: {str(e)}")


@receiver(post_save, sender=Borrowing)
def send_return_notification(sender, instance, **kwargs):
    """
    Send Telegram notification when a book is returned.
    """
    if not instance.pk:  # Skip for new instances
        return
    
    try:
        # Check if this is a return (actual_return_date was just set)
        old_instance = Borrowing.objects.get(pk=instance.pk)
        if old_instance.actual_return_date is None and instance.actual_return_date is not None:
            telegram_service = TelegramNotificationService()
            telegram_service.send_return_notification(instance)
    except Borrowing.DoesNotExist:
        pass
    except Exception as e:
        print(f"Failed to send return notification: {str(e)}")


@receiver(post_save, sender=Payment)
def send_payment_notification(sender, instance, created, **kwargs):
    """
    Send Telegram notification when a payment status changes.
    """
    if created:
        try:
            telegram_service = TelegramNotificationService()
            telegram_service.send_payment_notification(instance)
        except Exception as e:
            print(f"Failed to send payment notification: {str(e)}")
    else:
        # Check if status changed
        try:
            old_instance = Payment.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                telegram_service = TelegramNotificationService()
                telegram_service.send_payment_notification(instance)
        except Payment.DoesNotExist:
            pass
        except Exception as e:
            print(f"Failed to send payment status notification: {str(e)}")


def check_overdue_books():
    """
    Check for overdue books and send notifications.
    This function can be called by a scheduled task.
    """
    today = date.today()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lt=today,
        actual_return_date__isnull=True
    )
    
    telegram_service = TelegramNotificationService()
    
    for borrowing in overdue_borrowings:
        try:
            telegram_service.send_overdue_notification(borrowing)
        except Exception as e:
            print(f"Failed to send overdue notification for borrowing {borrowing.id}: {str(e)}")


def send_daily_summary():
    """
    Send daily summary notification.
    This function can be called by a scheduled task.
    """
    today = date.today()
    
    # Get today's statistics
    new_borrowings = Borrowing.objects.filter(borrow_date=today).count()
    returns = Borrowing.objects.filter(actual_return_date=today).count()
    payments = Payment.objects.filter(
        status='PAID',
        borrowing__borrow_date=today
    ).count()
    overdue = Borrowing.objects.filter(
        expected_return_date__lt=today,
        actual_return_date__isnull=True
    ).count()
    
    # Calculate revenue
    revenue = sum(
        payment.money_to_pay for payment in Payment.objects.filter(
            status='PAID',
            borrowing__borrow_date=today
        )
    )
    
    summary_data = {
        'new_borrowings': new_borrowings,
        'returns': returns,
        'payments': payments,
        'overdue': overdue,
        'revenue': revenue,
        'date': today.strftime('%Y-%m-%d')
    }
    
    try:
        telegram_service = TelegramNotificationService()
        telegram_service.send_daily_summary(summary_data)
    except Exception as e:
        print(f"Failed to send daily summary: {str(e)}")