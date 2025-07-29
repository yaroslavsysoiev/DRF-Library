from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    """Serializer for Book model."""
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'cover', 'inventory', 'daily_fee']
        read_only_fields = ['id']
    
    def validate_inventory(self, value):
        """Validate inventory is not negative."""
        if value < 0:
            raise serializers.ValidationError("Inventory cannot be negative.")
        return value
    
    def validate_daily_fee(self, value):
        """Validate daily fee is not negative."""
        if value < 0:
            raise serializers.ValidationError("Daily fee cannot be negative.")
        return value


class BookListSerializer(serializers.ModelSerializer):
    """Serializer for book list with availability status."""
    
    is_available = serializers.ReadOnlyField()
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'cover', 'inventory', 'daily_fee', 'is_available']