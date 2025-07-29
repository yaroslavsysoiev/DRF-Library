from rest_framework import generics
from rest_framework.response import Response

class BorrowingListView(generics.ListAPIView):
    """Temporary view for borrowings list."""
    
    def get(self, request, *args, **kwargs):
        return Response({"message": "Borrowings service coming soon!"})


class BorrowingDetailView(generics.RetrieveAPIView):
    """Temporary view for borrowing detail."""
    
    def get(self, request, *args, **kwargs):
        return Response({"message": "Borrowing detail coming soon!"})


class BorrowingReturnView(generics.GenericAPIView):
    """Temporary view for borrowing return."""
    
    def post(self, request, *args, **kwargs):
        return Response({"message": "Borrowing return coming soon!"})