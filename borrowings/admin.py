from django.contrib import admin
from .models import Borrowing


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    """Admin configuration for Borrowing model."""
    
    list_display = ('user', 'book', 'borrow_date', 'expected_return_date', 'actual_return_date', 'is_active', 'is_overdue')
    list_filter = ('borrow_date', 'expected_return_date', 'actual_return_date', 'book__author')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'book__title', 'book__author')
    ordering = ('-borrow_date',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Book Information', {
            'fields': ('book',)
        }),
        ('Dates', {
            'fields': ('borrow_date', 'expected_return_date', 'actual_return_date')
        }),
    )
    
    readonly_fields = ('borrow_date', 'is_active', 'is_overdue')
    
    def is_active(self, obj):
        """Display active status."""
        return obj.is_active
    is_active.boolean = True
    is_active.short_description = 'Active'
    
    def is_overdue(self, obj):
        """Display overdue status."""
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'