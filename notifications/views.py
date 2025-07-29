from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from datetime import date
from .services import TelegramNotificationService
from .signals import check_overdue_books, send_daily_summary


class TestNotificationView(generics.GenericAPIView):
    """View for testing Telegram notifications."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, *args, **kwargs):
        """Send a test notification."""
        try:
            telegram_service = TelegramNotificationService()
            
            # Send test message
            success = telegram_service.send_message(
                "🧪 <b>Test Notification</b>\n\n"
                "This is a test message from the DRF Library system.\n"
                f"Timestamp: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            if success:
                return Response({
                    "message": "Test notification sent successfully",
                    "timestamp": timezone.now().isoformat()
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "Failed to send test notification"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                "error": f"Error sending test notification: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckOverdueView(generics.GenericAPIView):
    """View for manually checking overdue books and sending notifications."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, *args, **kwargs):
        """Check for overdue books and send notifications."""
        try:
            check_overdue_books()
            
            return Response({
                "message": "Overdue books check completed",
                "timestamp": timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": f"Error checking overdue books: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DailySummaryView(generics.GenericAPIView):
    """View for manually sending daily summary."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, *args, **kwargs):
        """Send daily summary notification."""
        try:
            send_daily_summary()
            
            return Response({
                "message": "Daily summary sent successfully",
                "timestamp": timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": f"Error sending daily summary: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)