from datetime import date, timedelta
from decimal import Decimal
from django.conf import settings
from django.db.models import Q
from borrowings.models import Borrowing
from payments.models import Payment
from notifications.services import TelegramNotificationService


class FineCalculationService:
    """Service for calculating and managing fines for overdue books."""
    
    def __init__(self):
        self.fine_multiplier = getattr(settings, 'FINE_MULTIPLIER', 2.0)
    
    def calculate_fine_amount(self, borrowing: Borrowing) -> Decimal:
        """
        Calculate fine amount for an overdue borrowing.
        
        Args:
            borrowing: Borrowing instance
            
        Returns:
            Decimal: Fine amount
        """
        if not borrowing.is_overdue:
            return Decimal('0.00')
        
        overdue_days = borrowing.overdue_days
        daily_fee = borrowing.book.daily_fee
        
        # Calculate fine: daily_fee * overdue_days * multiplier
        fine_amount = daily_fee * overdue_days * Decimal(str(self.fine_multiplier))
        
        return fine_amount
    
    def get_overdue_borrowings(self) -> list:
        """
        Get all overdue borrowings.
        
        Returns:
            list: List of overdue borrowing instances
        """
        today = date.today()
        overdue_borrowings = Borrowing.objects.filter(
            expected_return_date__lt=today,
            actual_return_date__isnull=True
        ).select_related('user', 'book')
        
        return list(overdue_borrowings)
    
    def create_fine_payment(self, borrowing: Borrowing) -> Payment:
        """
        Create a fine payment for an overdue borrowing.
        
        Args:
            borrowing: Borrowing instance
            
        Returns:
            Payment: Created payment instance
        """
        fine_amount = self.calculate_fine_amount(borrowing)
        
        if fine_amount <= 0:
            raise ValueError("Cannot create fine payment for non-overdue borrowing")
        
        # Check if fine payment already exists
        existing_fine = Payment.objects.filter(
            borrowing=borrowing,
            type='FINE',
            status__in=['PENDING', 'PAID']
        ).first()
        
        if existing_fine:
            raise ValueError("Fine payment already exists for this borrowing")
        
        # Create fine payment
        fine_payment = Payment.objects.create(
            borrowing=borrowing,
            type='FINE',
            money_to_pay=fine_amount,
            status='PENDING'
        )
        
        return fine_payment
    
    def process_overdue_books(self) -> dict:
        """
        Process all overdue books and create fine payments.
        
        Returns:
            dict: Summary of processed fines
        """
        overdue_borrowings = self.get_overdue_borrowings()
        created_fines = []
        errors = []
        
        for borrowing in overdue_borrowings:
            try:
                # Check if fine already exists
                existing_fine = Payment.objects.filter(
                    borrowing=borrowing,
                    type='FINE'
                ).first()
                
                if not existing_fine:
                    fine_payment = self.create_fine_payment(borrowing)
                    created_fines.append(fine_payment)
                    
                    # Send notification
                    try:
                        telegram_service = TelegramNotificationService()
                        telegram_service.send_fine_notification(borrowing)
                    except Exception as e:
                        print(f"Failed to send fine notification: {str(e)}")
                        
            except Exception as e:
                errors.append({
                    'borrowing_id': borrowing.id,
                    'error': str(e)
                })
        
        return {
            'created_fines': len(created_fines),
            'errors': len(errors),
            'total_overdue': len(overdue_borrowings),
            'errors_details': errors
        }
    
    def get_fine_statistics(self) -> dict:
        """
        Get statistics about fines.
        
        Returns:
            dict: Fine statistics
        """
        today = date.today()
        
        # Total fines created today
        fines_today = Payment.objects.filter(
            type='FINE',
            borrowing__borrow_date__lte=today
        ).count()
        
        # Total fines paid today
        fines_paid_today = Payment.objects.filter(
            type='FINE',
            status='PAID',
            borrowing__borrow_date__lte=today
        ).count()
        
        # Total fine revenue
        total_fine_revenue = sum(
            payment.money_to_pay for payment in Payment.objects.filter(
                type='FINE',
                status='PAID'
            )
        )
        
        # Pending fines
        pending_fines = Payment.objects.filter(
            type='FINE',
            status='PENDING'
        ).count()
        
        # Overdue books without fines
        overdue_without_fines = Borrowing.objects.filter(
            expected_return_date__lt=today,
            actual_return_date__isnull=True
        ).exclude(
            payments__type='FINE'
        ).count()
        
        return {
            'fines_today': fines_today,
            'fines_paid_today': fines_paid_today,
            'total_fine_revenue': total_fine_revenue,
            'pending_fines': pending_fines,
            'overdue_without_fines': overdue_without_fines,
            'fine_multiplier': self.fine_multiplier
        }
    
    def waive_fine(self, borrowing: Borrowing, reason: str = None) -> bool:
        """
        Waive a fine for a borrowing (admin only).
        
        Args:
            borrowing: Borrowing instance
            reason: Reason for waiving the fine
            
        Returns:
            bool: True if fine was waived successfully
        """
        try:
            # Find existing fine payment
            fine_payment = Payment.objects.filter(
                borrowing=borrowing,
                type='FINE',
                status='PENDING'
            ).first()
            
            if fine_payment:
                fine_payment.status = 'EXPIRED'
                fine_payment.save()
                
                # Send notification about waived fine
                try:
                    telegram_service = TelegramNotificationService()
                    telegram_service.send_message(
                        f"💰 <b>Fine Waived</b>\n\n"
                        f"👤 User: {borrowing.user.get_full_name() or borrowing.user.email}\n"
                        f"📖 Book: {borrowing.book.title} by {borrowing.book.author}\n"
                        f"💰 Waived Amount: ${fine_payment.money_to_pay}\n"
                        f"📝 Reason: {reason or 'Admin decision'}\n\n"
                        f"ID: {borrowing.id}"
                    )
                except Exception as e:
                    print(f"Failed to send fine waiver notification: {str(e)}")
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error waiving fine: {str(e)}")
            return False
    
    def get_user_fines(self, user) -> list:
        """
        Get all fines for a specific user.
        
        Args:
            user: User instance
            
        Returns:
            list: List of fine payments for the user
        """
        return Payment.objects.filter(
            borrowing__user=user,
            type='FINE'
        ).select_related('borrowing', 'borrowing__book').order_by('-id')