"""
Message formatter module to convert Telegram messages to WhatsApp format
"""

import datetime
import re
from telethon.tl.types import (
    MessageMediaPhoto, MessageMediaDocument, MessageMediaWebPage,
    MessageMediaGeo, MessageMediaContact, MessageMediaGame,
    MessageMediaPoll, MessageMediaUnsupported, MessageMediaVenue,
    MessageMediaGeoLive, MessageMediaInvoice, MessageMediaDice
)


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
        if not message or (not message.text and not message.media):
            return None

        # Get message date
        date_str = self.format_date(message.date)

        # Get sender name
        if hasattr(message, 'sender') and message.sender:
            sender_name = getattr(message.sender, 'first_name', 'Unknown')
            if hasattr(message.sender, 'last_name') and message.sender.last_name:
                sender_name += f" {message.sender.last_name}"
        else:
            sender_name = "Unknown"

        # Format message content
        try:
            # Initialize edited_suffix
            edited_suffix = " <This message was edited>" if hasattr(
                message, 'edit_date') and message.edit_date else ""

            # Handle deleted messages
            if hasattr(message, 'deleted') and message.deleted:
                content = "This message was deleted"
                return f"{date_str} - {sender_name}: {content}"

            # Handle media messages
            if hasattr(message, 'media') and message.media:
                # Photo
                if isinstance(message.media, MessageMediaPhoto):
                    content = "<Media omitted>"

                # Document (file, video, audio, etc.)
                elif isinstance(message.media, MessageMediaDocument):
                    # Try to get the file name or mime type
                    if hasattr(message.media, 'document') and hasattr(message.media.document, 'attributes'):
                        for attr in message.media.document.attributes:
                            if hasattr(attr, 'file_name') and attr.file_name:
                                # It's a file with a name
                                content = f"<File: {attr.file_name} omitted>"
                                break
                    if not 'content' in locals() or content == "":
                        content = "<Media omitted>"

                # Web page/link preview
                elif isinstance(message.media, MessageMediaWebPage):
                    # If there's text, use it with the link
                    if message.text:
                        content = message.text
                    else:
                        content = "<Link omitted>"

                # Location
                elif any(isinstance(message.media, t) for t in [MessageMediaGeo, MessageMediaGeoLive, MessageMediaVenue]):
                    content = "<Location omitted>"

                # Contact
                elif isinstance(message.media, MessageMediaContact):
                    content = "<Contact omitted>"

                # Poll
                elif isinstance(message.media, MessageMediaPoll):
                    content = "<Poll omitted>"

                # Other media types
                else:
                    content = "<Media omitted>"

            # Text messages
            elif hasattr(message, 'text') and message.text:
                content = message.text

            # Empty or unknown message type
            else:
                content = ""
                return None  # Skip empty messages

        except Exception:
            content = "<Message format error>"
            edited_suffix = ""

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
        # Start with just the encryption header (like WhatsApp)
        formatted_messages = [self.format_chat_header(chat_title)]

        # Process messages in reverse order (oldest first, like WhatsApp)
        for message in reversed(messages):
            try:
                formatted = self.format_message(message, chat_title)
                if formatted:
                    formatted_messages.append(formatted)
            except Exception:
                # Skip messages that can't be formatted
                continue

        return formatted_messages
