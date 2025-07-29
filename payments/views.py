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
from .services import StripeService


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
    
    def create(self, request, *args, **kwargs):
        """Create payment and initialize Stripe session."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create payment instance
        payment = serializer.save()
        
        try:
            # Initialize Stripe service
            stripe_service = StripeService()
            
            # Create payment session
            session_data = stripe_service.create_payment_session(payment)
            
            return Response({
                'message': 'Payment session created successfully',
                'payment': PaymentDetailSerializer(payment).data,
                'stripe_session': {
                    'session_id': session_data['session_id'],
                    'session_url': session_data['session_url'],
                    'amount': session_data['amount']
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Delete payment if Stripe session creation fails
            payment.delete()
            return Response({
                'error': f'Failed to create payment session: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


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
            
            # Verify payment with Stripe
            stripe_service = StripeService()
            is_paid = stripe_service.verify_payment_session(session_id)
            
            if is_paid:
                payment.status = 'PAID'
                payment.save()
                
                return Response(
                    {
                        "message": "Payment completed successfully",
                        "payment": PaymentDetailSerializer(payment).data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Payment verification failed"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Payment verification error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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


class PaymentRefundView(generics.GenericAPIView):
    """View for creating refunds."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, *args, **kwargs):
        """Create a refund for a payment."""
        payment_id = kwargs.get('pk')
        
        try:
            payment = Payment.objects.get(id=payment_id)
            
            if payment.status != 'PAID':
                return Response(
                    {"error": "Only paid payments can be refunded"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get refund amount from request
            amount = request.data.get('amount')
            
            # Create refund
            stripe_service = StripeService()
            refund_data = stripe_service.create_refund(payment, amount)
            
            return Response({
                "message": "Refund created successfully",
                "refund": refund_data
            }, status=status.HTTP_200_OK)
            
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Refund creation failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )