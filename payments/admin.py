from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for Payment model."""
    
    list_display = ('id', 'user', 'book', 'type', 'status', 'money_to_pay', 'session_id')
    list_filter = ('status', 'type', 'borrowing__book__author')
    search_fields = ('borrowing__user__email', 'borrowing__user__first_name', 'borrowing__book__title', 'session_id')
    ordering = ('-id',)
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('status', 'type', 'money_to_pay')
        }),
        ('Stripe Information', {
            'fields': ('session_url', 'session_id')
        }),
        ('Borrowing Information', {
            'fields': ('borrowing',)
        }),
    )
    
    readonly_fields = ('user', 'book')
    
    def user(self, obj):
        """Display user from borrowing."""
        return obj.user
    user.short_description = 'User'
    
    def book(self, obj):
        """Display book from borrowing."""
        return obj.book
    book.short_description = 'Book'