"""
Tests for the WhatsAppFormatter class
"""

import unittest
import datetime
from unittest.mock import Mock, patch
from chatshift.formatter import WhatsAppFormatter

class TestWhatsAppFormatter(unittest.TestCase):
    """Test cases for WhatsAppFormatter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.formatter = WhatsAppFormatter(user_id=12345)
    
    def test_format_date(self):
        """Test date formatting"""
        date = datetime.datetime(2023, 6, 1, 21, 10)
        formatted = self.formatter.format_date(date)
        self.assertEqual(formatted, "01/06/23, 21:10")
    
    def test_format_chat_header(self):
        """Test chat header formatting"""
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.datetime(2023, 6, 1, 21, 10)
            header = self.formatter.format_chat_header("Test Chat")
            self.assertIn("01/06/23, 21:10", header)
            self.assertIn("Messages and calls are end-to-end encrypted", header)
    
    def test_format_text_message(self):
        """Test formatting a text message"""
        # Create a mock message
        message = Mock()
        message.text = "Hello, world!"
        message.media = None
        message.date = datetime.datetime(2023, 6, 1, 21, 10)
        message.deleted = False
        message.edit_date = None
        
        # Create a mock sender
        sender = Mock()
        sender.first_name = "John"
        sender.last_name = "Doe"
        sender.id = 67890
        message.sender = sender
        
        formatted = self.formatter.format_message(message, "Test Chat")
        self.assertEqual(formatted, "01/06/23, 21:10 - John Doe: Hello, world!")
    
    def test_format_deleted_message(self):
        """Test formatting a deleted message"""
        # Create a mock message
        message = Mock()
        message.text = "Original text"
        message.media = None
        message.date = datetime.datetime(2023, 6, 1, 21, 10)
        message.deleted = True
        message.edit_date = None
        
        # Create a mock sender
        sender = Mock()
        sender.first_name = "John"
        sender.last_name = "Doe"
        sender.id = 67890
        message.sender = sender
        
        formatted = self.formatter.format_message(message, "Test Chat")
        self.assertEqual(formatted, "01/06/23, 21:10 - John Doe: This message was deleted")
    
    def test_format_edited_message(self):
        """Test formatting an edited message"""
        # Create a mock message
        message = Mock()
        message.text = "Edited text"
        message.media = None
        message.date = datetime.datetime(2023, 6, 1, 21, 10)
        message.deleted = False
        message.edit_date = datetime.datetime(2023, 6, 1, 21, 15)
        
        # Create a mock sender
        sender = Mock()
        sender.first_name = "John"
        sender.last_name = "Doe"
        sender.id = 67890
        message.sender = sender
        
        formatted = self.formatter.format_message(message, "Test Chat")
        self.assertEqual(formatted, "01/06/23, 21:10 - John Doe: Edited text <This message was edited>")
    
    def test_format_media_message(self):
        """Test formatting a media message"""
        # Create a mock message
        message = Mock()
        message.text = None
        message.date = datetime.datetime(2023, 6, 1, 21, 10)
        message.deleted = False
        message.edit_date = None
        
        # Create a mock media
        media = Mock()
        message.media = media
        
        # Create a mock sender
        sender = Mock()
        sender.first_name = "John"
        sender.last_name = "Doe"
        sender.id = 67890
        message.sender = sender
        
        # Test with different media types
        from telethon.tl.types import MessageMediaPhoto
        message.media = MessageMediaPhoto(None, None)
        formatted = self.formatter.format_message(message, "Test Chat")
        self.assertEqual(formatted, "01/06/23, 21:10 - John Doe: <Media omitted>")

if __name__ == '__main__':
    unittest.main()
