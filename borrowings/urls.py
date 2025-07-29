from django.urls import path
from . import views

app_name = 'borrowings'

urlpatterns = [
    path('', views.BorrowingListView.as_view(), name='borrowing-list'),
    path('<int:pk>/', views.BorrowingDetailView.as_view(), name='borrowing-detail'),
    path('<int:pk>/return/', views.BorrowingReturnView.as_view(), name='borrowing-return'),
]