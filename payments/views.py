from rest_framework import generics
from rest_framework.response import Response

class PaymentListView(generics.ListAPIView):
    """Temporary view for payments list."""
    
    def get(self, request, *args, **kwargs):
        return Response({"message": "Payments service coming soon!"})


class PaymentDetailView(generics.RetrieveAPIView):
    """Temporary view for payment detail."""
    
    def get(self, request, *args, **kwargs):
        return Response({"message": "Payment detail coming soon!"})


class PaymentSuccessView(generics.GenericAPIView):
    """Temporary view for payment success."""
    
    def get(self, request, *args, **kwargs):
        return Response({"message": "Payment success coming soon!"})


class PaymentCancelView(generics.GenericAPIView):
    """Temporary view for payment cancel."""
    
    def get(self, request, *args, **kwargs):
        return Response({"message": "Payment cancel coming soon!"})