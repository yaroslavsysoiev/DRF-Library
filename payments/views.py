from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db.models import Q
from .models import Payment
from .serializers import (
    PaymentListSerializer, 
    PaymentDetailSerializer, 
    PaymentCreateSerializer
)
from .permissions import PaymentPermissions, PaymentCreatePermissions


class PaymentListView(generics.ListCreateAPIView):
    """View for listing and creating payments."""
    
    permission_classes = [PaymentCreatePermissions]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'type']
    ordering_fields = ['id', 'money_to_pay', 'status']
    ordering = ['-id']
    
    def get_queryset(self):
        """Filter payments based on user permissions."""
        user = self.request.user
        
        if user.is_staff:
            # Admin can see all payments
            queryset = Payment.objects.all()
        else:
            # Regular users can only see their own payments
            queryset = Payment.objects.filter(borrowing__user=user)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PaymentListSerializer
        return PaymentCreateSerializer
    
    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class PaymentDetailView(generics.RetrieveAPIView):
    """View for retrieving payment details."""
    
    queryset = Payment.objects.all()
    serializer_class = PaymentDetailSerializer
    permission_classes = [PaymentPermissions]


class PaymentSuccessView(generics.GenericAPIView):
    """View for handling successful Stripe payments."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        """Handle successful payment callback from Stripe."""
        session_id = request.GET.get('session_id')
        
        if not session_id:
            return Response(
                {"error": "No session_id provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            payment = Payment.objects.get(session_id=session_id)
            payment.status = 'PAID'
            payment.save()
            
            return Response(
                {
                    "message": "Payment completed successfully",
                    "payment": PaymentDetailSerializer(payment).data
                },
                status=status.HTTP_200_OK
            )
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class PaymentCancelView(generics.GenericAPIView):
    """View for handling cancelled Stripe payments."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        """Handle cancelled payment callback from Stripe."""
        return Response(
            {
                "message": "Payment was cancelled. You can complete the payment later.",
                "note": "Payment session is available for 24 hours."
            },
            status=status.HTTP_200_OK
        )