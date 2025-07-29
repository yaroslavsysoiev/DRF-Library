from django.urls import path
from . import views
from . import fine_views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='payment-list'),
    path('<int:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('success/', views.PaymentSuccessView.as_view(), name='success'),
    path('cancel/', views.PaymentCancelView.as_view(), name='cancel'),
    path('<int:pk>/refund/', views.PaymentRefundView.as_view(), name='refund'),
    
    # Fine endpoints
    path('fines/', fine_views.FineListView.as_view(), name='fine-list'),
    path('fines/<int:pk>/', fine_views.FineDetailView.as_view(), name='fine-detail'),
    path('fines/process/', fine_views.ProcessFinesView.as_view(), name='process-fines'),
    path('fines/statistics/', fine_views.FineStatisticsView.as_view(), name='fine-statistics'),
    path('fines/waive/', fine_views.WaiveFineView.as_view(), name='waive-fine'),
    path('fines/my/', fine_views.UserFinesView.as_view(), name='user-fines'),
]