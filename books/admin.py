from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin configuration for Book model."""
    
    list_display = ('title', 'author', 'cover', 'inventory', 'daily_fee', 'is_available')
    list_filter = ('cover', 'author')
    search_fields = ('title', 'author')
    ordering = ('title',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'cover')
        }),
        ('Inventory & Pricing', {
            'fields': ('inventory', 'daily_fee')
        }),
    )
    
    readonly_fields = ('is_available',)
    
    def is_available(self, obj):
        """Display availability status."""
        return obj.is_available
    is_available.boolean = True
    is_available.short_description = 'Available'