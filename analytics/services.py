from datetime import date, timedelta
from django.db.models import Q, Sum, Count, Avg, Max, Min
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from django.utils import timezone
from borrowings.models import Borrowing
from payments.models import Payment
from books.models import Book
from users.models import User


class AnalyticsService:
    """Service for advanced library analytics."""
    
    def __init__(self):
        self.today = date.today()
    
    def get_revenue_analytics(self, period_days: int = 30) -> dict:
        """
        Get comprehensive revenue analytics.
        
        Args:
            period_days: Number of days to analyze
            
        Returns:
            dict: Revenue analytics data
        """
        start_date = self.today - timedelta(days=period_days)
        
        # Daily revenue
        daily_revenue = Payment.objects.filter(
            status='PAID',
            borrowing__borrow_date__gte=start_date
        ).annotate(
            date=TruncDate('borrowing__borrow_date')
        ).values('date').annotate(
            total=Sum('money_to_pay'),
            count=Count('id')
        ).order_by('date')
        
        # Revenue by type
        revenue_by_type = Payment.objects.filter(
            status='PAID',
            borrowing__borrow_date__gte=start_date
        ).values('type').annotate(
            total=Sum('money_to_pay'),
            count=Count('id')
        )
        
        # Total revenue
        total_revenue = sum(item['total'] for item in daily_revenue)
        total_payments = sum(item['count'] for item in daily_revenue)
        
        # Average daily revenue
        avg_daily_revenue = total_revenue / period_days if period_days > 0 else 0
        
        return {
            'period_days': period_days,
            'start_date': start_date,
            'end_date': self.today,
            'total_revenue': total_revenue,
            'total_payments': total_payments,
            'avg_daily_revenue': avg_daily_revenue,
            'daily_revenue': list(daily_revenue),
            'revenue_by_type': list(revenue_by_type)
        }
    
    def get_borrowing_analytics(self, period_days: int = 30) -> dict:
        """
        Get comprehensive borrowing analytics.
        
        Args:
            period_days: Number of days to analyze
            
        Returns:
            dict: Borrowing analytics data
        """
        start_date = self.today - timedelta(days=period_days)
        
        # Daily borrowings
        daily_borrowings = Borrowing.objects.filter(
            borrow_date__gte=start_date
        ).annotate(
            date=TruncDate('borrow_date')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Borrowing trends
        borrowing_trends = Borrowing.objects.filter(
            borrow_date__gte=start_date
        ).annotate(
            month=TruncMonth('borrow_date')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Return rate
        total_borrowings = Borrowing.objects.filter(
            borrow_date__gte=start_date
        ).count()
        
        returned_books = Borrowing.objects.filter(
            borrow_date__gte=start_date,
            actual_return_date__isnull=False
        ).count()
        
        return_rate = (returned_books / total_borrowings * 100) if total_borrowings > 0 else 0
        
        # Average borrowing duration
        completed_borrowings = Borrowing.objects.filter(
            borrow_date__gte=start_date,
            actual_return_date__isnull=False
        )
        
        avg_duration = completed_borrowings.aggregate(
            avg_days=Avg(
                timezone.now().date() - F('borrow_date')
            )
        )['avg_days'] or 0
        
        return {
            'period_days': period_days,
            'total_borrowings': total_borrowings,
            'returned_books': returned_books,
            'return_rate': return_rate,
            'avg_borrowing_duration': avg_duration,
            'daily_borrowings': list(daily_borrowings),
            'borrowing_trends': list(borrowing_trends)
        }
    
    def get_book_analytics(self) -> dict:
        """
        Get comprehensive book analytics.
        
        Returns:
            dict: Book analytics data
        """
        # Most popular books
        popular_books = Book.objects.annotate(
            borrow_count=Count('borrowings')
        ).order_by('-borrow_count')[:10]
        
        # Books by author
        books_by_author = Book.objects.values('author').annotate(
            book_count=Count('id'),
            total_borrowings=Count('borrowings')
        ).order_by('-total_borrowings')
        
        # Books by cover type
        books_by_cover = Book.objects.values('cover').annotate(
            count=Count('id'),
            total_borrowings=Count('borrowings')
        )
        
        # Average daily fee
        avg_daily_fee = Book.objects.aggregate(
            avg_fee=Avg('daily_fee')
        )['avg_fee'] or 0
        
        # Inventory analytics
        total_inventory = Book.objects.aggregate(
            total=Sum('inventory')
        )['total'] or 0
        
        available_books = Book.objects.filter(inventory__gt=0).count()
        
        return {
            'popular_books': list(popular_books.values('id', 'title', 'author', 'borrow_count')),
            'books_by_author': list(books_by_author),
            'books_by_cover': list(books_by_cover),
            'avg_daily_fee': avg_daily_fee,
            'total_inventory': total_inventory,
            'available_books': available_books
        }
    
    def get_user_analytics(self) -> dict:
        """
        Get comprehensive user analytics.
        
        Returns:
            dict: User analytics data
        """
        # Most active users
        active_users = User.objects.annotate(
            borrow_count=Count('borrowings'),
            payment_count=Count('borrowings__payments'),
            total_spent=Sum('borrowings__payments__money_to_pay')
        ).filter(
            borrow_count__gt=0
        ).order_by('-borrow_count')[:10]
        
        # User registration trends
        registration_trends = User.objects.annotate(
            month=TruncMonth('date_joined')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # User statistics
        total_users = User.objects.count()
        active_users_count = User.objects.filter(
            borrowings__isnull=False
        ).distinct().count()
        
        # Users with overdue books
        users_with_overdue = User.objects.filter(
            borrowings__expected_return_date__lt=self.today,
            borrowings__actual_return_date__isnull=True
        ).distinct().count()
        
        return {
            'active_users': list(active_users.values('id', 'email', 'first_name', 'last_name', 'borrow_count', 'payment_count', 'total_spent')),
            'registration_trends': list(registration_trends),
            'total_users': total_users,
            'active_users_count': active_users_count,
            'users_with_overdue': users_with_overdue
        }
    
    def get_fine_analytics(self, period_days: int = 30) -> dict:
        """
        Get comprehensive fine analytics.
        
        Args:
            period_days: Number of days to analyze
            
        Returns:
            dict: Fine analytics data
        """
        start_date = self.today - timedelta(days=period_days)
        
        # Fine statistics
        total_fines = Payment.objects.filter(
            type='FINE',
            borrowing__borrow_date__gte=start_date
        ).count()
        
        paid_fines = Payment.objects.filter(
            type='FINE',
            status='PAID',
            borrowing__borrow_date__gte=start_date
        ).count()
        
        pending_fines = Payment.objects.filter(
            type='FINE',
            status='PENDING'
        ).count()
        
        # Fine revenue
        fine_revenue = Payment.objects.filter(
            type='FINE',
            status='PAID',
            borrowing__borrow_date__gte=start_date
        ).aggregate(
            total=Sum('money_to_pay')
        )['total'] or 0
        
        # Average fine amount
        avg_fine_amount = Payment.objects.filter(
            type='FINE',
            status='PAID',
            borrowing__borrow_date__gte=start_date
        ).aggregate(
            avg=Avg('money_to_pay')
        )['avg'] or 0
        
        # Fine payment rate
        fine_payment_rate = (paid_fines / total_fines * 100) if total_fines > 0 else 0
        
        return {
            'period_days': period_days,
            'total_fines': total_fines,
            'paid_fines': paid_fines,
            'pending_fines': pending_fines,
            'fine_revenue': fine_revenue,
            'avg_fine_amount': avg_fine_amount,
            'fine_payment_rate': fine_payment_rate
        }
    
    def get_overdue_analytics(self) -> dict:
        """
        Get comprehensive overdue analytics.
        
        Returns:
            dict: Overdue analytics data
        """
        # Overdue statistics
        overdue_borrowings = Borrowing.objects.filter(
            expected_return_date__lt=self.today,
            actual_return_date__isnull=True
        )
        
        total_overdue = overdue_borrowings.count()
        
        # Overdue by days
        overdue_by_days = {}
        for borrowing in overdue_borrowings:
            days_overdue = (self.today - borrowing.expected_return_date).days
            overdue_by_days[days_overdue] = overdue_by_days.get(days_overdue, 0) + 1
        
        # Average overdue days
        avg_overdue_days = overdue_borrowings.aggregate(
            avg_days=Avg(
                self.today - F('expected_return_date')
            )
        )['avg_days'] or 0
        
        # Overdue books by user
        overdue_by_user = overdue_borrowings.values('user__email').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return {
            'total_overdue': total_overdue,
            'avg_overdue_days': avg_overdue_days,
            'overdue_by_days': overdue_by_days,
            'overdue_by_user': list(overdue_by_user)
        }
    
    def get_comprehensive_report(self, period_days: int = 30) -> dict:
        """
        Get comprehensive analytics report.
        
        Args:
            period_days: Number of days to analyze
            
        Returns:
            dict: Comprehensive analytics report
        """
        return {
            'period': {
                'days': period_days,
                'start_date': self.today - timedelta(days=period_days),
                'end_date': self.today
            },
            'revenue': self.get_revenue_analytics(period_days),
            'borrowings': self.get_borrowing_analytics(period_days),
            'books': self.get_book_analytics(),
            'users': self.get_user_analytics(),
            'fines': self.get_fine_analytics(period_days),
            'overdue': self.get_overdue_analytics(),
            'generated_at': timezone.now().isoformat()
        }