#!/usr/bin/env python3
"""
ChatShift - Export Telegram chats to WhatsApp-like format

This is the main entry point for the ChatShift application.
Run this file to start the application.

Author: mosaddiX
Version: 0.4.0
"""

import os
import sys
import time
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import User, Chat, Channel, Dialog

# Rich terminal components
from rich.console import Console, Group
from rich.panel import Panel
from rich.progress import Progress, TextColumn, BarColumn, SpinnerColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.style import Style
from rich.theme import Theme
from rich.live import Live
from rich.align import Align
from rich.box import ROUNDED, DOUBLE, HEAVY

# Additional styling
import colorama
from colorama import Fore, Back, Style as ColoramaStyle
from termcolor import colored
import pyfiglet

# Initialize colorama
colorama.init(autoreset=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create a custom theme for Rich
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "bold green",
    "title": "bold blue",
    "subtitle": "italic cyan",
    "highlight": "bold yellow",
    "user": "bold cyan",
    "group": "bold green",
    "channel": "bold magenta",
    "unread": "bold red",
})

# Create a console with the custom theme
console = Console(theme=custom_theme, highlight=True)

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
    """Elegant CLI for ChatShift"""

    def __init__(self):
        """Initialize the CLI"""
        self.client = None
        self.dialogs = []
        self.spinner_chars = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']

    def display_logo(self):
        """Display the ChatShift logo"""
        # Create a fancy logo with pyfiglet
        logo = pyfiglet.figlet_format("ChatShift", font="slant")
        colored_logo = ""

        # Add gradient coloring to the logo
        colors = [Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
        lines = logo.split('\n')
        for i, line in enumerate(lines):
            color_index = i % len(colors)
            colored_logo += colors[color_index] + line + '\n'

        # Print the logo
        print(colored_logo)

        # Display version and tagline
        version_text = Text("v0.4.0", style="italic cyan")
        tagline = Text("Telegram to WhatsApp Chat Exporter", style="italic")
        author = Text("Developed by mosaddiX", style="dim")

        # Create a panel with the version info
        panel = Panel(
            Group(
                Align.center(version_text),
                Align.center(tagline),
                Align.center(author)
            ),
            box=ROUNDED,
            border_style="cyan",
            padding=(1, 4)
        )

        # Display the panel
        console.print(panel)

    async def authenticate(self):
        """Authenticate with Telegram"""
        # Create an authentication panel
        auth_panel = Panel(
            "[bold]Telegram Authentication[/bold]\n\n"
            "Connecting to Telegram servers...",
            title="Authentication",
            border_style="cyan",
            box=ROUNDED
        )
        console.print(auth_panel)

        # Create the client
        self.client = TelegramClient('chatshift_session', API_ID, API_HASH)

        # Connect to Telegram with a spinner
        with console.status("[bold cyan]Connecting to Telegram...[/bold cyan]", spinner="dots") as status:
            await self.client.connect()
            status.update("[bold green]Connected![/bold green]")
            time.sleep(0.5)

        # Check if already authenticated
        if not await self.client.is_user_authorized():
            console.print(f"[bold]Logging in as[/bold] [cyan]{PHONE}[/cyan]")

            # Send code request with a spinner
            with console.status("[bold cyan]Sending authentication code...[/bold cyan]", spinner="dots") as status:
                await self.client.send_code_request(PHONE)
                status.update("[bold green]Code sent![/bold green]")
                time.sleep(0.5)

            # Ask for the code with a styled prompt
            code = console.input(
                "\n[bold]Enter the code you received:[/bold] ")

            try:
                # Sign in with the code (with spinner)
                with console.status("[bold cyan]Verifying code...[/bold cyan]", spinner="dots") as status:
                    await self.client.sign_in(PHONE, code)
                    status.update(
                        "[bold green]Verification successful![/bold green]")
                    time.sleep(0.5)
            except Exception as e:
                console.print(
                    f"[bold red]Error during authentication:[/bold red] {str(e)}")
                return False

        # Success message
        console.print(
            "[bold green]✓ Successfully authenticated with Telegram![/bold green]")
        return True

    async def get_dialogs(self):
        """Get all dialogs (chats)"""
        # Create a panel for the dialog fetching process
        fetch_panel = Panel(
            "[bold]Fetching Your Chats[/bold]\n\n"
            "Retrieving your Telegram conversations...",
            title="Chats",
            border_style="cyan",
            box=ROUNDED
        )
        console.print(fetch_panel)

        try:
            # Get all dialogs with a spinner
            with console.status("[bold cyan]Retrieving chats from Telegram...[/bold cyan]", spinner="dots") as status:
                self.dialogs = await self.client.get_dialogs()
                status.update(
                    f"[bold green]Found {len(self.dialogs)} chats![/bold green]")
                time.sleep(0.5)
            return True
        except Exception as e:
            console.print(
                f"[bold red]Error fetching chats:[/bold red] {str(e)}")
            return False

    def display_dialogs(self):
        """Display all dialogs in a numbered list"""
        # Create a table for the dialogs
        table = Table(
            title="Your Telegram Chats",
            box=ROUNDED,
            border_style="cyan",
            header_style="bold cyan",
            show_lines=True,
            title_style="bold cyan",
            expand=True
        )

        # Add columns
        table.add_column("ID", justify="center", style="dim", width=4)
        table.add_column("Type", justify="center", width=10)
        table.add_column("Name", width=40)
        table.add_column("Unread", justify="center", width=8)

        # Add rows for each dialog
        for i, dialog in enumerate(self.dialogs, 1):
            entity = dialog.entity

            # Determine entity type and style
            if isinstance(entity, User):
                entity_type = "👤 User"
                type_style = "user"
            elif isinstance(entity, Chat):
                entity_type = "👥 Group"
                type_style = "group"
            else:
                entity_type = "📢 Channel"
                type_style = "channel"

            # Format unread count
            if dialog.unread_count > 0:
                unread = f"[unread]{dialog.unread_count}[/unread]"
            else:
                unread = "0"

            # Add row to table
            table.add_row(
                str(i),
                f"[{type_style}]{entity_type}[/{type_style}]",
                dialog.name,
                unread
            )

        # Print the table
        console.print(table)

    def select_dialog(self):
        """Let the user select a dialog"""
        # Create a styled prompt
        options_panel = Panel(
            "[bold]Options:[/bold]\n\n"
            "• Enter a [cyan]number[/cyan] to select a chat\n"
            "• Enter [cyan]r[/cyan] to refresh the chat list\n"
            "• Enter [cyan]q[/cyan] to quit",
            title="Chat Selection",
            border_style="cyan",
            box=ROUNDED,
            width=40
        )
        console.print(options_panel)

        while True:
            try:
                # Styled input prompt
                choice = console.input("\n[bold]Enter your choice:[/bold] ")

                if choice.lower() == 'q':
                    console.print("[dim]Exiting...[/dim]")
                    return None
                elif choice.lower() == 'r':
                    console.print("[dim]Refreshing chats...[/dim]")
                    return 'refresh'

                choice = int(choice)
                if 1 <= choice <= len(self.dialogs):
                    selected = self.dialogs[choice - 1]
                    console.print(
                        f"[bold green]Selected:[/bold green] [cyan]{selected.name}[/cyan]")
                    return selected
                else:
                    console.print(
                        f"[bold yellow]Please enter a number between 1 and {len(self.dialogs)}.[/bold yellow]")
            except ValueError:
                console.print(
                    "[bold yellow]Please enter a valid number.[/bold yellow]")

    def get_export_options(self):
        """Get export options from the user"""
        # Create a panel for export options
        export_panel = Panel(
            "[bold]Export Configuration[/bold]",
            title="Export Options",
            border_style="cyan",
            box=ROUNDED
        )
        console.print(export_panel)

        # Get message limit with validation
        while True:
            try:
                # Styled input for message limit
                limit_input = console.input(
                    f"[bold]Message limit[/bold] [dim](default: {DEFAULT_MESSAGE_LIMIT}, 0 for all):[/dim] ")
                limit = int(
                    limit_input) if limit_input else DEFAULT_MESSAGE_LIMIT

                if limit < 0:
                    console.print(
                        "[bold yellow]Please enter a positive number.[/bold yellow]")
                    continue

                # Show confirmation of the limit
                if limit == 0:
                    console.print(
                        "[dim]→ Will export[/dim] [cyan]all messages[/cyan]")
                else:
                    console.print(
                        f"[dim]→ Will export up to[/dim] [cyan]{limit} messages[/cyan]")
                break
            except ValueError:
                console.print(
                    "[bold yellow]Please enter a valid number.[/bold yellow]")

        # Get output file with styled input
        output_file = console.input(
            f"\n[bold]Output file[/bold] [dim](default: {DEFAULT_OUTPUT_FILE}):[/dim] ")

        if not output_file:
            output_file = DEFAULT_OUTPUT_FILE

        # Show confirmation of the output file
        console.print(f"[dim]→ Will save to[/dim] [cyan]{output_file}[/cyan]")

        return {
            'limit': limit,
            'output_file': output_file
        }

    async def export_chat(self, dialog, limit, output_file):
        """Export a chat to WhatsApp format"""
        # Create an export panel with details
        export_panel = Panel(
            f"[bold]Exporting Chat:[/bold] [cyan]{dialog.name}[/cyan]\n"
            f"[bold]Message Limit:[/bold] [cyan]{limit if limit > 0 else 'All'}[/cyan]\n"
            f"[bold]Output File:[/bold] [cyan]{output_file}[/cyan]",
            title="Export Details",
            border_style="cyan",
            box=ROUNDED
        )
        console.print(export_panel)

        # Set a reasonable default if limit is 0
        actual_limit = 5000 if limit == 0 else limit

        try:
            # Create a progress display
            with console.status("[bold cyan]Preparing to download messages...[/bold cyan]", spinner="dots") as status:
                # Initialize counters
                messages = []
                message_count = 0

                # Show progress message
                status.update("[bold cyan]Downloading messages...[/bold cyan]")

                # Download messages with progress updates
                async for message in self.client.iter_messages(dialog.entity, limit=actual_limit):
                    # Include all non-empty messages
                    if message:
                        messages.append(message)

                    # Update progress
                    message_count += 1
                    if message_count % 50 == 0:
                        status.update(
                            f"[bold cyan]Downloaded {message_count} messages...[/bold cyan]")

                # Show completion message
                status.update(
                    f"[bold green]Downloaded {message_count} messages![/bold green]")
                time.sleep(0.5)

                # Format messages
                status.update("[bold cyan]Formatting messages...[/bold cyan]")
                formatted_messages = await self.format_messages(messages, dialog.name)
                time.sleep(0.5)

                # Write to file
                status.update("[bold cyan]Writing to file...[/bold cyan]")
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(formatted_messages))
                time.sleep(0.5)

                # Show completion message
                status.update(
                    "[bold green]Export completed successfully![/bold green]")
                time.sleep(0.5)

            # Show success message with details
            success_panel = Panel(
                f"[bold green]✓ Export completed successfully![/bold green]\n\n"
                f"[bold]Messages Exported:[/bold] [cyan]{len(messages)}[/cyan]\n"
                f"[bold]Output File:[/bold] [cyan]{output_file}[/cyan]",
                title="Success",
                border_style="green",
                box=ROUNDED
            )
            console.print(success_panel)

            # Ask if user wants to open the file
            open_file = console.input(
                "\n[bold]Do you want to open the file?[/bold] (y/n): ")
            if open_file.lower() == 'y':
                with console.status("[bold cyan]Opening file...[/bold cyan]", spinner="dots"):
                    self.open_file(output_file)
                    time.sleep(0.5)

            return True
        except Exception as e:
            # Show error message
            error_panel = Panel(
                f"[bold red]Error exporting chat:[/bold red]\n{str(e)}",
                title="Error",
                border_style="red",
                box=ROUNDED
            )
            console.print(error_panel)
            return False

    def open_file(self, file_path):
        """Open a file with the default application"""
        try:
            # Import platform-specific modules
            import platform
            import subprocess

            # Different approach based on platform
            system = platform.system()

            if system == 'Windows':
                # Windows
                os.startfile(file_path)
            elif system == 'Darwin':
                # macOS
                subprocess.call(['open', file_path])
            elif system == 'Linux':
                # Linux
                subprocess.call(['xdg-open', file_path])
            else:
                # Unknown OS
                console.print(
                    "[bold yellow]Unsupported operating system.[/bold yellow]")

        except Exception as e:
            console.print(
                f"[bold red]Failed to open file:[/bold red] {str(e)}")

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
        # Clear the screen for a clean start
        os.system('cls' if os.name == 'nt' else 'clear')

        # Display the logo
        self.display_logo()

        # Authenticate with Telegram
        if not await self.authenticate():
            console.print(
                "\n[bold red]Authentication failed. Exiting...[/bold red]")
            return

        # Main loop
        while True:
            # Get dialogs
            if not await self.get_dialogs():
                console.print(
                    "\n[bold red]Failed to fetch chats. Exiting...[/bold red]")
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
            another = console.input(
                "\n[bold]Do you want to export another chat?[/bold] (y/n): ")
            if another.lower() != 'y':
                break

        # Disconnect from Telegram
        if self.client:
            with console.status("[bold cyan]Disconnecting from Telegram...[/bold cyan]", spinner="dots") as status:
                await self.client.disconnect()
                time.sleep(0.5)
                status.update("[bold green]Disconnected![/bold green]")
                time.sleep(0.5)

        # Farewell message
        farewell_panel = Panel(
            "[bold green]Thank you for using ChatShift![/bold green]\n\n"
            "[italic]Your chats have been exported successfully.[/italic]",
            title="Goodbye",
            border_style="cyan",
            box=ROUNDED
        )
        console.print(farewell_panel)


async def main():
    """Main function"""
    cli = ChatShiftCLI()
    await cli.run()

if __name__ == "__main__":
    # Run the CLI
    asyncio.run(main())
