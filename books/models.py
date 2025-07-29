from django.db import models


class Book(models.Model):
    """Book model for library inventory management."""
    
    COVER_CHOICES = [
        ('HARD', 'Hardcover'),
        ('SOFT', 'Softcover'),
    ]
    
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=4, choices=COVER_CHOICES, default='HARD')
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    @property
    def is_available(self):
        """Check if book is available for borrowing."""
        return self.inventory > 0