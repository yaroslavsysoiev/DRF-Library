from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Payment
from .serializers import PaymentListSerializer, PaymentDetailSerializer
from .fine_service import FineCalculationService
from .permissions import PaymentPermissions


class FineListView(generics.ListAPIView):
    """View for listing fines."""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentListSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['id', 'money_to_pay', 'status']
    ordering = ['-id']
    
    def get_queryset(self):
        """Filter fines based on user permissions."""
        user = self.request.user
        
        if user.is_staff:
            # Admin can see all fines
            queryset = Payment.objects.filter(type='FINE')
        else:
            # Regular users can only see their own fines
            queryset = Payment.objects.filter(
                type='FINE',
                borrowing__user=user
            )
        
        return queryset


class FineDetailView(generics.RetrieveAPIView):
    """View for retrieving fine details."""
    
    queryset = Payment.objects.filter(type='FINE')
    serializer_class = PaymentDetailSerializer
    permission_classes = [PaymentPermissions]


class ProcessFinesView(generics.GenericAPIView):
    """View for processing overdue books and creating fines."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, *args, **kwargs):
        """Process overdue books and create fines."""
        try:
            fine_service = FineCalculationService()
            result = fine_service.process_overdue_books()
            
            return Response({
                "message": "Fine processing completed",
                "summary": result,
                "timestamp": result.get('timestamp')
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": f"Error processing fines: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FineStatisticsView(generics.GenericAPIView):
    """View for getting fine statistics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        """Get fine statistics."""
        try:
            fine_service = FineCalculationService()
            statistics = fine_service.get_fine_statistics()
            
            return Response({
                "statistics": statistics
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": f"Error getting fine statistics: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WaiveFineView(generics.GenericAPIView):
    """View for waiving fines."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, *args, **kwargs):
        """Waive a fine for a borrowing."""
        borrowing_id = request.data.get('borrowing_id')
        reason = request.data.get('reason', 'Admin decision')
        
        if not borrowing_id:
            return Response({
                "error": "borrowing_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from borrowings.models import Borrowing
            borrowing = Borrowing.objects.get(id=borrowing_id)
            
            fine_service = FineCalculationService()
            success = fine_service.waive_fine(borrowing, reason)
            
            if success:
                return Response({
                    "message": "Fine waived successfully",
                    "borrowing_id": borrowing_id,
                    "reason": reason
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "No pending fine found for this borrowing"
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Borrowing.DoesNotExist:
            return Response({
                "error": "Borrowing not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": f"Error waiving fine: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserFinesView(generics.ListAPIView):
    """View for getting user's fines."""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentListSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['id', 'money_to_pay', 'status']
    ordering = ['-id']
    
    def get_queryset(self):
        """Get fines for the current user."""
        user = self.request.user
        fine_service = FineCalculationService()
        return fine_service.get_user_fines(user)