from rest_framework import generics, permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Book
from .serializers import BookSerializer, BookListSerializer
from .permissions import BookPermissions


class BookListView(generics.ListCreateAPIView):
    """View for listing and creating books."""
    
    queryset = Book.objects.all()
    permission_classes = [BookPermissions]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['cover', 'author']
    search_fields = ['title', 'author']
    ordering_fields = ['title', 'author', 'daily_fee', 'inventory']
    ordering = ['title']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BookListSerializer
        return BookSerializer


class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating and deleting books."""
    
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [BookPermissions]