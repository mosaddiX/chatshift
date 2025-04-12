#!/usr/bin/env python3
"""
ChatShift CLI - A simple terminal-based Telegram to WhatsApp chat exporter
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import User, Chat, Channel, Dialog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Telegram API credentials
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE = os.getenv('TELEGRAM_PHONE')
USERNAME = os.getenv('TELEGRAM_USERNAME')

# Default export settings
DEFAULT_OUTPUT_FILE = os.getenv('OUTPUT_FILE', 'telegram_chat_export.txt')
DEFAULT_MESSAGE_LIMIT = int(os.getenv('MESSAGE_LIMIT', '5000'))

class ChatShiftCLI:
    """Simple CLI for ChatShift"""
    
    def __init__(self):
        """Initialize the CLI"""
        self.client = None
        self.dialogs = []
        
    async def authenticate(self):
        """Authenticate with Telegram"""
        print("\n=== Telegram Authentication ===")
        
        # Create the client
        self.client = TelegramClient('chatshift_session', API_ID, API_HASH)
        
        # Connect to Telegram
        await self.client.connect()
        
        # Check if already authenticated
        if not await self.client.is_user_authorized():
            print(f"Logging in as {PHONE}...")
            
            # Send code request
            await self.client.send_code_request(PHONE)
            
            # Ask for the code
            code = input("Enter the code you received: ")
            
            try:
                # Sign in with the code
                await self.client.sign_in(PHONE, code)
            except Exception as e:
                print(f"Error during authentication: {str(e)}")
                return False
        
        print("Successfully authenticated with Telegram!")
        return True
    
    async def get_dialogs(self):
        """Get all dialogs (chats)"""
        print("\nFetching your chats...")
        
        try:
            # Get all dialogs
            self.dialogs = await self.client.get_dialogs()
            print(f"Found {len(self.dialogs)} chats.")
            return True
        except Exception as e:
            print(f"Error fetching chats: {str(e)}")
            return False
    
    def display_dialogs(self):
        """Display all dialogs in a numbered list"""
        print("\n=== Your Telegram Chats ===")
        
        # Display header
        print(f"{'ID':<4} {'Type':<8} {'Name':<40} {'Unread':<6}")
        print("-" * 60)
        
        # Display each dialog
        for i, dialog in enumerate(self.dialogs, 1):
            entity = dialog.entity
            
            # Determine entity type
            if isinstance(entity, User):
                entity_type = "User"
            elif isinstance(entity, Chat):
                entity_type = "Group"
            else:
                entity_type = "Channel"
            
            # Format unread count
            unread = f"{dialog.unread_count}" if dialog.unread_count > 0 else "0"
            
            # Print dialog info
            print(f"{i:<4} {entity_type:<8} {dialog.name:<40} {unread:<6}")
    
    def select_dialog(self):
        """Let the user select a dialog"""
        while True:
            try:
                choice = input("\nEnter the ID of the chat to export (or 'r' to refresh, 'q' to quit): ")
                
                if choice.lower() == 'q':
                    return None
                elif choice.lower() == 'r':
                    return 'refresh'
                
                choice = int(choice)
                if 1 <= choice <= len(self.dialogs):
                    return self.dialogs[choice - 1]
                else:
                    print(f"Please enter a number between 1 and {len(self.dialogs)}.")
            except ValueError:
                print("Please enter a valid number.")
    
    def get_export_options(self):
        """Get export options from the user"""
        print("\n=== Export Options ===")
        
        # Get message limit
        while True:
            try:
                limit_input = input(f"Message limit (default: {DEFAULT_MESSAGE_LIMIT}, 0 for all): ")
                limit = int(limit_input) if limit_input else DEFAULT_MESSAGE_LIMIT
                if limit < 0:
                    print("Please enter a positive number.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")
        
        # Get output file
        output_file = input(f"Output file (default: {DEFAULT_OUTPUT_FILE}): ")
        if not output_file:
            output_file = DEFAULT_OUTPUT_FILE
        
        return {
            'limit': limit,
            'output_file': output_file
        }
    
    async def export_chat(self, dialog, limit, output_file):
        """Export a chat to WhatsApp format"""
        print(f"\nExporting chat: {dialog.name}")
        print(f"Message limit: {limit}")
        print(f"Output file: {output_file}")
        
        # Set a reasonable default if limit is 0
        actual_limit = 5000 if limit == 0 else limit
        
        try:
            # Get messages
            print("Downloading messages...")
            messages = []
            message_count = 0
            
            async for message in self.client.iter_messages(dialog.entity, limit=actual_limit):
                # Include all non-empty messages
                if message:
                    messages.append(message)
                
                # Update progress
                message_count += 1
                if message_count % 100 == 0:
                    print(f"Downloaded {message_count} messages...")
            
            print(f"Downloaded {message_count} messages.")
            
            # Format messages in WhatsApp style
            print("Formatting messages...")
            formatted_messages = await self.format_messages(messages, dialog.name)
            
            # Write to file
            print("Writing to file...")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(formatted_messages))
            
            print(f"\nExport completed successfully!")
            print(f"Exported {len(messages)} messages to {output_file}")
            
            # Ask if user wants to open the file
            open_file = input("Do you want to open the file? (y/n): ")
            if open_file.lower() == 'y':
                self.open_file(output_file)
            
            return True
        except Exception as e:
            print(f"Error exporting chat: {str(e)}")
            return False
    
    def open_file(self, file_path):
        """Open a file with the default application"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS and Linux
                import subprocess
                try:
                    # Try the Linux command first
                    subprocess.run(['xdg-open', file_path], check=False)
                except FileNotFoundError:
                    try:
                        # Try the macOS command
                        subprocess.run(['open', file_path], check=False)
                    except FileNotFoundError:
                        print("Could not find a program to open the file.")
        except Exception as e:
            print(f"Failed to open file: {str(e)}")
    
    def format_date(self, date):
        """Format date in WhatsApp style: DD/MM/YY, HH:MM"""
        return date.strftime("%d/%m/%y, %H:%M")
    
    async def format_message(self, message, chat_title=None):
        """Format a single message in WhatsApp style"""
        # Skip empty messages
        if not message:
            return None
        
        try:
            # Get message date
            date_str = self.format_date(message.date)
            
            # Get sender name
            if hasattr(message, 'sender') and message.sender:
                if hasattr(message.sender, 'first_name') and message.sender.first_name:
                    sender_name = message.sender.first_name
                    if hasattr(message.sender, 'last_name') and message.sender.last_name:
                        sender_name += f" {message.sender.last_name}"
                elif hasattr(message.sender, 'title') and message.sender.title:
                    sender_name = message.sender.title
                else:
                    sender_name = "Unknown"
            else:
                sender_name = "Unknown"
            
            # Check if message was edited
            edited_suffix = " (edited)" if message.edit_date else ""
            
            # Get message content
            if hasattr(message, 'media') and message.media:
                # Media message
                content = "<Media omitted>"
            elif hasattr(message, 'text') and message.text:
                # Text message
                content = message.text
            elif hasattr(message, 'action') and message.action:
                # Service message (e.g., someone joined the group)
                action_type = type(message.action).__name__
                if 'ChatCreate' in action_type:
                    content = "created this group"
                elif 'ChatAddUser' in action_type:
                    content = "added a participant to the group"
                elif 'ChatDeleteUser' in action_type:
                    content = "removed a participant from the group"
                elif 'ChatJoinedByLink' in action_type:
                    content = "joined the group by link"
                elif 'ChatEditTitle' in action_type:
                    content = f"changed the group name to {getattr(message.action, 'title', 'unknown')}"
                elif 'ChatEditPhoto' in action_type:
                    content = "changed the group photo"
                elif 'ChatDeletePhoto' in action_type:
                    content = "removed the group photo"
                elif 'MessagePin' in action_type:
                    content = "pinned a message"
                else:
                    content = f"performed action: {action_type}"
            else:
                # Empty or unknown message type
                content = "<Message>"
        except Exception as e:
            content = "<Message format error>"
            edited_suffix = ""
        
        # Format in WhatsApp style
        return f"{date_str} - {sender_name}: {content}{edited_suffix}"
    
    def format_chat_header(self, chat_title):
        """Format chat header in WhatsApp style"""
        today = datetime.now()
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
                formatted = await self.format_message(message, chat_title)
                if formatted:
                    formatted_messages.append(formatted)
            except Exception as e:
                logger.error(f"Error formatting message: {str(e)}")
        
        return formatted_messages
    
    async def run(self):
        """Run the CLI"""
        print("\n=== ChatShift CLI v0.4.0 ===")
        print("Telegram to WhatsApp Chat Exporter")
        print("Developed by mosaddiX")
        
        # Authenticate with Telegram
        if not await self.authenticate():
            print("Authentication failed. Exiting...")
            return
        
        # Main loop
        while True:
            # Get dialogs
            if not await self.get_dialogs():
                print("Failed to fetch chats. Exiting...")
                break
            
            # Display dialogs
            self.display_dialogs()
            
            # Select dialog
            selected_dialog = self.select_dialog()
            
            if selected_dialog is None:
                # User wants to quit
                break
            elif selected_dialog == 'refresh':
                # User wants to refresh
                continue
            
            # Get export options
            options = self.get_export_options()
            
            # Export chat
            await self.export_chat(selected_dialog, options['limit'], options['output_file'])
            
            # Ask if user wants to export another chat
            another = input("\nDo you want to export another chat? (y/n): ")
            if another.lower() != 'y':
                break
        
        # Disconnect from Telegram
        if self.client:
            await self.client.disconnect()
        
        print("\nThank you for using ChatShift CLI!")

async def main():
    """Main function"""
    cli = ChatShiftCLI()
    await cli.run()

if __name__ == "__main__":
    # Run the CLI
    asyncio.run(main())
