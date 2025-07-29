import stripe
from django.conf import settings
from django.urls import reverse
from .models import Payment


class StripeService:
    """Service for handling Stripe payment operations."""
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
    
    def create_payment_session(self, payment: Payment) -> dict:
        """
        Create a Stripe checkout session for payment.
        
        Args:
            payment: Payment instance
            
        Returns:
            dict: Session data with URL and ID
        """
        try:
            # Calculate payment amount
            amount = payment.calculate_payment_amount()
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"{payment.type} - {payment.book.title}",
                            'description': f"Payment for borrowing: {payment.borrowing.id}",
                        },
                        'unit_amount': int(amount * 100),  # Convert to cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=settings.SITE_URL + reverse('payments:success') + f'?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=settings.SITE_URL + reverse('payments:cancel'),
                metadata={
                    'payment_id': payment.id,
                    'borrowing_id': payment.borrowing.id,
                    'user_id': payment.user.id,
                }
            )
            
            # Update payment with session data
            payment.session_id = session.id
            payment.session_url = session.url
            payment.money_to_pay = amount
            payment.save()
            
            return {
                'session_id': session.id,
                'session_url': session.url,
                'amount': amount
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error creating payment session: {str(e)}")
    
    def verify_payment_session(self, session_id: str) -> bool:
        """
        Verify if a payment session was successful.
        
        Args:
            session_id: Stripe session ID
            
        Returns:
            bool: True if payment was successful
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session.payment_status == 'paid'
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    def get_payment_intent(self, session_id: str) -> dict:
        """
        Get payment intent details from session.
        
        Args:
            session_id: Stripe session ID
            
        Returns:
            dict: Payment intent details
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_intent:
                intent = stripe.PaymentIntent.retrieve(session.payment_intent)
                return {
                    'id': intent.id,
                    'amount': intent.amount / 100,  # Convert from cents
                    'status': intent.status,
                    'currency': intent.currency,
                }
            return None
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    def create_refund(self, payment: Payment, amount: float = None) -> dict:
        """
        Create a refund for a payment.
        
        Args:
            payment: Payment instance
            amount: Amount to refund (None for full refund)
            
        Returns:
            dict: Refund details
        """
        try:
            if not payment.session_id:
                raise Exception("No session ID found for payment")
            
            session = stripe.checkout.Session.retrieve(payment.session_id)
            if not session.payment_intent:
                raise Exception("No payment intent found")
            
            refund_data = {
                'payment_intent': session.payment_intent,
            }
            
            if amount:
                refund_data['amount'] = int(amount * 100)  # Convert to cents
            
            refund = stripe.Refund.create(**refund_data)
            
            return {
                'id': refund.id,
                'amount': refund.amount / 100,
                'status': refund.status,
                'currency': refund.currency,
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error creating refund: {str(e)}")