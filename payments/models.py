from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class Payment(models.Model):
    """Payment model for handling Stripe payments."""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('EXPIRED', 'Expired'),
    ]
    
    TYPE_CHOICES = [
        ('PAYMENT', 'Payment'),
        ('FINE', 'Fine'),
    ]
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='PAYMENT')
    borrowing = models.ForeignKey('borrowings.Borrowing', on_delete=models.CASCADE, related_name='payments')
    session_url = models.URLField(max_length=500, blank=True)
    session_id = models.CharField(max_length=255, blank=True)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-id']
    
    def __str__(self):
        return f"Payment {self.id} - {self.status} - ${self.money_to_pay}"
    
    @property
    def user(self):
        """Get user from borrowing."""
        return self.borrowing.user
    
    @property
    def book(self):
        """Get book from borrowing."""
        return self.borrowing.book
    
    def calculate_payment_amount(self):
        """Calculate payment amount based on borrowing."""
        if self.type == 'PAYMENT':
            # Calculate based on borrowing duration
            from datetime import date
            days_borrowed = (self.borrowing.expected_return_date - self.borrowing.borrow_date).days
            return self.borrowing.book.daily_fee * days_borrowed
        elif self.type == 'FINE':
            # Calculate fine based on overdue days
            overdue_days = self.borrowing.overdue_days
            from django.conf import settings
            fine_multiplier = getattr(settings, 'FINE_MULTIPLIER', 2.0)
            return self.borrowing.book.daily_fee * overdue_days * Decimal(str(fine_multiplier))
        return Decimal('0.00')