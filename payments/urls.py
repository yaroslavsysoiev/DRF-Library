from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='payment-list'),
    path('<int:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('success/', views.PaymentSuccessView.as_view(), name='payment-success'),
    path('cancel/', views.PaymentCancelView.as_view(), name='payment-cancel'),
]