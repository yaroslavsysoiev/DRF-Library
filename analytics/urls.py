from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('revenue/', views.RevenueAnalyticsView.as_view(), name='revenue'),
    path('borrowings/', views.BorrowingAnalyticsView.as_view(), name='borrowings'),
    path('books/', views.BookAnalyticsView.as_view(), name='books'),
    path('users/', views.UserAnalyticsView.as_view(), name='users'),
    path('fines/', views.FineAnalyticsView.as_view(), name='fines'),
    path('overdue/', views.OverdueAnalyticsView.as_view(), name='overdue'),
    path('comprehensive/', views.ComprehensiveReportView.as_view(), name='comprehensive'),
    path('dashboard/', views.dashboard_summary, name='dashboard'),
    path('user-dashboard/', views.user_dashboard, name='user-dashboard'),
]