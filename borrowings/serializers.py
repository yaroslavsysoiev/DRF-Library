from rest_framework import serializers
from .models import Borrowing
from books.serializers import BookSerializer


class BorrowingListSerializer(serializers.ModelSerializer):
    """Serializer for borrowing list with book details."""
    
    book = BookSerializer(read_only=True)
    is_active = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    overdue_days = serializers.ReadOnlyField()
    
    class Meta:
        model = Borrowing
        fields = [
            'id', 'borrow_date', 'expected_return_date', 'actual_return_date',
            'book', 'user', 'is_active', 'is_overdue', 'overdue_days'
        ]
        read_only_fields = ['id', 'borrow_date', 'user', 'is_active', 'is_overdue', 'overdue_days']


class BorrowingDetailSerializer(serializers.ModelSerializer):
    """Serializer for borrowing detail with full book information."""
    
    book = BookSerializer(read_only=True)
    is_active = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    overdue_days = serializers.ReadOnlyField()
    
    class Meta:
        model = Borrowing
        fields = [
            'id', 'borrow_date', 'expected_return_date', 'actual_return_date',
            'book', 'user', 'is_active', 'is_overdue', 'overdue_days'
        ]
        read_only_fields = ['id', 'borrow_date', 'user', 'is_active', 'is_overdue', 'overdue_days']


class BorrowingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new borrowings."""
    
    class Meta:
        model = Borrowing
        fields = ['book', 'expected_return_date']
    
    def validate_book(self, value):
        """Validate book is available for borrowing."""
        if value.inventory <= 0:
            raise serializers.ValidationError("This book is not available for borrowing.")
        return value
    
    def validate_expected_return_date(self, value):
        """Validate expected return date is in the future."""
        from datetime import date
        if value <= date.today():
            raise serializers.ValidationError("Expected return date must be in the future.")
        return value


class BorrowingReturnSerializer(serializers.ModelSerializer):
    """Serializer for returning books."""
    
    class Meta:
        model = Borrowing
        fields = ['actual_return_date']
    
    def validate_actual_return_date(self, value):
        """Validate return date is not in the past."""
        from datetime import date
        if value < date.today():
            raise serializers.ValidationError("Return date cannot be in the past.")
        return value