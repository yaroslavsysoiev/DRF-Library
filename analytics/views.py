from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from .services import AnalyticsService
from django.db.models import Sum


class RevenueAnalyticsView(generics.GenericAPIView):
    """View for revenue analytics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        """Get revenue analytics."""
        try:
            period_days = int(request.GET.get('period_days', 30))
            analytics_service = AnalyticsService()
            revenue_data = analytics_service.get_revenue_analytics(period_days)
            
            return Response({
                "analytics": revenue_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": f"Error getting revenue analytics: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BorrowingAnalyticsView(generics.GenericAPIView):
    """View for borrowing analytics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        """Get borrowing analytics."""
        try:
            period_days = int(request.GET.get('period_days', 30))
            analytics_service = AnalyticsService()
            borrowing_data = analytics_service.get_borrowing_analytics(period_days)
            
            return Response({
                "analytics": borrowing_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": f"Error getting borrowing analytics: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookAnalyticsView(generics.GenericAPIView):
    """View for book analytics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        """Get book analytics."""
        try:
            analytics_service = AnalyticsService()
            book_data = analytics_service.get_book_analytics()
            
            return Response({
                "analytics": book_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": f"Error getting book analytics: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserAnalyticsView(generics.GenericAPIView):
    """View for user analytics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        """Get user analytics."""
        try:
            analytics_service = AnalyticsService()
            user_data = analytics_service.get_user_analytics()
            
            return Response({
                "analytics": user_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": f"Error getting user analytics: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FineAnalyticsView(generics.GenericAPIView):
    """View for fine analytics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        """Get fine analytics."""
        try:
            period_days = int(request.GET.get('period_days', 30))
            analytics_service = AnalyticsService()
            fine_data = analytics_service.get_fine_analytics(period_days)
            
            return Response({
                "analytics": fine_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": f"Error getting fine analytics: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OverdueAnalyticsView(generics.GenericAPIView):
    """View for overdue analytics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        """Get overdue analytics."""
        try:
            analytics_service = AnalyticsService()
            overdue_data = analytics_service.get_overdue_analytics()
            
            return Response({
                "analytics": overdue_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": f"Error getting overdue analytics: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ComprehensiveReportView(generics.GenericAPIView):
    """View for comprehensive analytics report."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        """Get comprehensive analytics report."""
        try:
            period_days = int(request.GET.get('period_days', 30))
            analytics_service = AnalyticsService()
            report_data = analytics_service.get_comprehensive_report(period_days)
            
            return Response({
                "report": report_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": f"Error generating comprehensive report: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def dashboard_summary(request):
    """Get dashboard summary for admin."""
    try:
        analytics_service = AnalyticsService()
        
        # Quick summary data
        revenue_data = analytics_service.get_revenue_analytics(7)  # Last 7 days
        borrowing_data = analytics_service.get_borrowing_analytics(7)
        overdue_data = analytics_service.get_overdue_analytics()
        
        summary = {
            'revenue_7_days': revenue_data['total_revenue'],
            'borrowings_7_days': borrowing_data['total_borrowings'],
            'overdue_books': overdue_data['total_overdue'],
            'return_rate': borrowing_data['return_rate'],
            'avg_daily_revenue': revenue_data['avg_daily_revenue']
        }
        
        return Response({
            "summary": summary
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "error": f"Error getting dashboard summary: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard(request):
    """Get user dashboard data."""
    try:
        user = request.user
        analytics_service = AnalyticsService()
        
        # User-specific data
        user_borrowings = user.borrowings.count()
        user_payments = user.borrowings.aggregate(
            total_spent=Sum('payments__money_to_pay')
        )['total_spent'] or 0
        
        user_overdue = user.borrowings.filter(
            expected_return_date__lt=analytics_service.today,
            actual_return_date__isnull=True
        ).count()
        
        user_data = {
            'total_borrowings': user_borrowings,
            'total_spent': user_payments,
            'overdue_books': user_overdue,
            'active_borrowings': user.borrowings.filter(
                actual_return_date__isnull=True
            ).count()
        }
        
        return Response({
            "user_dashboard": user_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "error": f"Error getting user dashboard: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)