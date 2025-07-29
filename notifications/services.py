import asyncio
import logging
from telegram import Bot
from telegram.error import TelegramError
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class TelegramNotificationService:
    """Service for sending Telegram notifications."""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        
        if not self.bot_token:
            raise ImproperlyConfigured("TELEGRAM_BOT_TOKEN is not set")
        if not self.chat_id:
            raise ImproperlyConfigured("TELEGRAM_CHAT_ID is not set")
        
        self.bot = Bot(token=self.bot_token)
    
    def send_message(self, message: str) -> bool:
        """
        Send a message to Telegram.
        
        Args:
            message: Message to send
            
        Returns:
            bool: True if message was sent successfully
        """
        try:
            # Use asyncio to run the async bot.send_message
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode='HTML'
                )
            )
            
            loop.close()
            logger.info(f"Telegram message sent successfully: {message[:50]}...")
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending Telegram message: {str(e)}")
            return False
    
    def send_borrowing_notification(self, borrowing) -> bool:
        """
        Send notification about new borrowing.
        
        Args:
            borrowing: Borrowing instance
            
        Returns:
            bool: True if notification was sent successfully
        """
        message = (
            f"📚 <b>New Book Borrowed</b>\n\n"
            f"👤 User: {borrowing.user.get_full_name() or borrowing.user.email}\n"
            f"📖 Book: {borrowing.book.title} by {borrowing.book.author}\n"
            f"📅 Borrow Date: {borrowing.borrow_date}\n"
            f"📅 Expected Return: {borrowing.expected_return_date}\n"
            f"💰 Daily Fee: ${borrowing.book.daily_fee}\n\n"
            f"ID: {borrowing.id}"
        )
        
        return self.send_message(message)
    
    def send_return_notification(self, borrowing) -> bool:
        """
        Send notification about book return.
        
        Args:
            borrowing: Borrowing instance
            
        Returns:
            bool: True if notification was sent successfully
        """
        message = (
            f"📚 <b>Book Returned</b>\n\n"
            f"👤 User: {borrowing.user.get_full_name() or borrowing.user.email}\n"
            f"📖 Book: {borrowing.book.title} by {borrowing.book.author}\n"
            f"📅 Return Date: {borrowing.actual_return_date}\n"
            f"📅 Expected Return: {borrowing.expected_return_date}\n\n"
            f"ID: {borrowing.id}"
        )
        
        return self.send_message(message)
    
    def send_overdue_notification(self, borrowing) -> bool:
        """
        Send notification about overdue book.
        
        Args:
            borrowing: Borrowing instance
            
        Returns:
            bool: True if notification was sent successfully
        """
        overdue_days = borrowing.overdue_days
        fine_amount = borrowing.book.daily_fee * overdue_days * 2  # 2x multiplier
        
        message = (
            f"⚠️ <b>Overdue Book Alert</b>\n\n"
            f"👤 User: {borrowing.user.get_full_name() or borrowing.user.email}\n"
            f"📖 Book: {borrowing.book.title} by {borrowing.book.author}\n"
            f"📅 Expected Return: {borrowing.expected_return_date}\n"
            f"⏰ Overdue Days: {overdue_days}\n"
            f"💰 Fine Amount: ${fine_amount}\n\n"
            f"ID: {borrowing.id}"
        )
        
        return self.send_message(message)
    
    def send_payment_notification(self, payment) -> bool:
        """
        Send notification about payment.
        
        Args:
            payment: Payment instance
            
        Returns:
            bool: True if notification was sent successfully
        """
        status_emoji = {
            'PENDING': '⏳',
            'PAID': '✅',
            'EXPIRED': '❌'
        }
        
        message = (
            f"💳 <b>Payment {status_emoji.get(payment.status, '❓')}</b>\n\n"
            f"👤 User: {payment.user.get_full_name() or payment.user.email}\n"
            f"📖 Book: {payment.book.title} by {payment.book.author}\n"
            f"💰 Amount: ${payment.money_to_pay}\n"
            f"📋 Type: {payment.type}\n"
            f"📊 Status: {payment.status}\n\n"
            f"ID: {payment.id}"
        )
        
        return self.send_message(message)
    
    def send_fine_notification(self, borrowing) -> bool:
        """
        Send notification about fine creation.
        
        Args:
            borrowing: Borrowing instance
            
        Returns:
            bool: True if notification was sent successfully
        """
        overdue_days = borrowing.overdue_days
        fine_amount = borrowing.book.daily_fee * overdue_days * 2  # 2x multiplier
        
        message = (
            f"💰 <b>Fine Created</b>\n\n"
            f"👤 User: {borrowing.user.get_full_name() or borrowing.user.email}\n"
            f"📖 Book: {borrowing.book.title} by {borrowing.book.author}\n"
            f"⏰ Overdue Days: {overdue_days}\n"
            f"💰 Fine Amount: ${fine_amount}\n"
            f"📅 Expected Return: {borrowing.expected_return_date}\n\n"
            f"ID: {borrowing.id}"
        )
        
        return self.send_message(message)
    
    def send_daily_summary(self, summary_data: dict) -> bool:
        """
        Send daily summary notification.
        
        Args:
            summary_data: Dictionary with summary data
            
        Returns:
            bool: True if notification was sent successfully
        """
        message = (
            f"📊 <b>Daily Library Summary</b>\n\n"
            f"📚 New Borrowings: {summary_data.get('new_borrowings', 0)}\n"
            f"📖 Returns: {summary_data.get('returns', 0)}\n"
            f"💳 Payments: {summary_data.get('payments', 0)}\n"
            f"⚠️ Overdue Books: {summary_data.get('overdue', 0)}\n"
            f"💰 Revenue: ${summary_data.get('revenue', 0)}\n\n"
            f"📅 Date: {summary_data.get('date', 'N/A')}"
        )
        
        return self.send_message(message)