from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db.models import Q
from datetime import date
from .models import Borrowing
from .serializers import (
    BorrowingListSerializer, 
    BorrowingDetailSerializer, 
    BorrowingCreateSerializer,
    BorrowingReturnSerializer
)
from .permissions import BorrowingPermissions, BorrowingCreatePermissions


class BorrowingListView(generics.ListCreateAPIView):
    """View for listing and creating borrowings."""
    
    permission_classes = [BorrowingCreatePermissions]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_active']
    ordering_fields = ['borrow_date', 'expected_return_date', 'actual_return_date']
    ordering = ['-borrow_date']
    
    def get_queryset(self):
        """Filter borrowings based on user permissions."""
        user = self.request.user
        
        if user.is_staff:
            # Admin can see all borrowings
            queryset = Borrowing.objects.all()
            
            # Filter by user_id if provided
            user_id = self.request.query_params.get('user_id')
            if user_id:
                queryset = queryset.filter(user_id=user_id)
        else:
            # Regular users can only see their own borrowings
            queryset = Borrowing.objects.filter(user=user)
        
        # Filter by is_active if provided
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            if is_active_bool:
                queryset = queryset.filter(actual_return_date__isnull=True)
            else:
                queryset = queryset.filter(actual_return_date__isnull=False)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BorrowingListSerializer
        return BorrowingCreateSerializer
    
    def perform_create(self, serializer):
        """Set the current user when creating a borrowing."""
        serializer.save(user=self.request.user)


class BorrowingDetailView(generics.RetrieveAPIView):
    """View for retrieving borrowing details."""
    
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingDetailSerializer
    permission_classes = [BorrowingPermissions]


class BorrowingReturnView(generics.UpdateAPIView):
    """View for returning books."""
    
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReturnSerializer
    permission_classes = [BorrowingPermissions]
    http_method_names = ['post']
    
    def update(self, request, *args, **kwargs):
        """Override update to handle book return."""
        borrowing = self.get_object()
        
        # Check if already returned
        if borrowing.actual_return_date is not None:
            return Response(
                {"error": "This book has already been returned."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set return date to today
        borrowing.actual_return_date = date.today()
        borrowing.save()
        
        return Response(
            {
                "message": "Book returned successfully",
                "borrowing": BorrowingDetailSerializer(borrowing).data
            },
            status=status.HTTP_200_OK
        )
