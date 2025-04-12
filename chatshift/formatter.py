"""
Message formatter module to convert Telegram messages to WhatsApp format
"""

import os
import datetime
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, MessageMediaWebPage

class WhatsAppFormatter:
    """Format Telegram messages to WhatsApp-like format"""
    
    def __init__(self, user_id=None):
        """Initialize formatter with user ID for identifying own messages"""
        self.user_id = user_id
    
    def format_date(self, date):
        """Format date in WhatsApp style: DD/MM/YY, HH:MM"""
        return date.strftime("%d/%m/%y, %H:%M")
    
    def format_message(self, message, chat_title=None):
        """Format a single message in WhatsApp style"""
        # Skip empty messages
        if not message.text and not message.media:
            return None
        
        # Get message date
        date_str = self.format_date(message.date)
        
        # Get sender name
        if message.sender:
            sender_name = message.sender.first_name
            if message.sender.last_name:
                sender_name += f" {message.sender.last_name}"
        else:
            sender_name = "Unknown"
        
        # Format message content
        if message.media:
            if isinstance(message.media, MessageMediaPhoto):
                content = "<Media omitted>"
            elif isinstance(message.media, MessageMediaDocument):
                content = "<Media omitted>"
            elif isinstance(message.media, MessageMediaWebPage):
                content = message.text or "<Link omitted>"
            else:
                content = "<Media omitted>"
        else:
            content = message.text
        
        # Handle deleted messages
        if message.deleted:
            content = "This message was deleted"
        
        # Handle edited messages
        edited_suffix = " <This message was edited>" if message.edit_date else ""
        
        # Format in WhatsApp style
        return f"{date_str} - {sender_name}: {content}{edited_suffix}"
    
    def format_chat_header(self, chat_title):
        """Format chat header in WhatsApp style"""
        today = datetime.datetime.now()
        date_str = self.format_date(today)
        
        return (
            f"{date_str} - Messages and calls are end-to-end encrypted. "
            f"No one outside of this chat, not even WhatsApp, can read or listen to them. "
            f"Tap to learn more."
        )
    
    async def format_messages(self, messages, chat_title):
        """Format a list of messages in WhatsApp style"""
        formatted_messages = [self.format_chat_header(chat_title)]
        
        for message in messages:
            formatted = self.format_message(message, chat_title)
            if formatted:
                formatted_messages.append(formatted)
        
        return formatted_messages
