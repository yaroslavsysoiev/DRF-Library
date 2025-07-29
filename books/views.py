from rest_framework import generics
from rest_framework.response import Response

class BookListView(generics.ListAPIView):
    """Temporary view for books list."""
    
    def get(self, request, *args, **kwargs):
        return Response({"message": "Books service coming soon!"})


class BookDetailView(generics.RetrieveAPIView):
    """Temporary view for book detail."""
    
    def get(self, request, *args, **kwargs):
        return Response({"message": "Book detail coming soon!"})