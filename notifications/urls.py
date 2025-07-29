from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('test/', views.TestNotificationView.as_view(), name='test'),
    path('overdue/', views.CheckOverdueView.as_view(), name='overdue'),
    path('summary/', views.DailySummaryView.as_view(), name='summary'),
]