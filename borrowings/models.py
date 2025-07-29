from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import date

User = get_user_model()


class Borrowing(models.Model):
    """Borrowing model for tracking book borrowings."""
    
    borrow_date = models.DateField(default=date.today)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE, related_name='borrowings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowings')
    
    class Meta:
        verbose_name = 'Borrowing'
        verbose_name_plural = 'Borrowings'
        ordering = ['-borrow_date']
    
    def __str__(self):
        return f"{self.user.email} borrowed {self.book.title} on {self.borrow_date}"
    
    @property
    def is_active(self):
        """Check if borrowing is still active (not returned)."""
        return self.actual_return_date is None
    
    @property
    def is_overdue(self):
        """Check if borrowing is overdue."""
        if self.is_active and self.expected_return_date < date.today():
            return True
        return False
    
    @property
    def overdue_days(self):
        """Calculate number of overdue days."""
        if self.is_overdue:
            return (date.today() - self.expected_return_date).days
        return 0
    
    def save(self, *args, **kwargs):
        """Override save to handle inventory changes."""
        is_new = self.pk is None
        
        if is_new:
            # Check if book is available
            if self.book.inventory <= 0:
                raise ValueError("Book is not available for borrowing")
            
            # Decrease inventory
            self.book.inventory -= 1
            self.book.save()
        else:
            # Handle return
            old_instance = Borrowing.objects.get(pk=self.pk)
            if old_instance.actual_return_date is None and self.actual_return_date is not None:
                # Book is being returned
                self.book.inventory += 1
                self.book.save()
        
        super().save(*args, **kwargs)