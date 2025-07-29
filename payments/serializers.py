from rest_framework import serializers
from .models import Payment
from borrowings.serializers import BorrowingDetailSerializer


class PaymentListSerializer(serializers.ModelSerializer):
    """Serializer for payment list with borrowing details."""
    
    borrowing = BorrowingDetailSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'status', 'type', 'borrowing', 'session_url', 
            'session_id', 'money_to_pay'
        ]
        read_only_fields = ['id', 'session_url', 'session_id']


class PaymentDetailSerializer(serializers.ModelSerializer):
    """Serializer for payment detail with full borrowing information."""
    
    borrowing = BorrowingDetailSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'status', 'type', 'borrowing', 'session_url', 
            'session_id', 'money_to_pay'
        ]
        read_only_fields = ['id', 'session_url', 'session_id']


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments."""
    
    class Meta:
        model = Payment
        fields = ['borrowing', 'type', 'money_to_pay']
    
    def validate_borrowing(self, value):
        """Validate borrowing exists and belongs to user."""
        user = self.context['request'].user
        if value.user != user and not user.is_staff:
            raise serializers.ValidationError("You can only create payments for your own borrowings.")
        return value
    
    def validate_money_to_pay(self, value):
        """Validate payment amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be positive.")
        return value