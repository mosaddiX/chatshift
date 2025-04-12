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
from rich.box import ROUNDED, DOUBLE, HEAVY, MINIMAL
from rich.layout import Layout
from rich.columns import Columns

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

# Create a custom theme for Rich - premium and elegant
custom_theme = Theme({
    # Base colors
    "info": "dim #8be9fd",  # Soft cyan
    "warning": "#bd93f9",   # Soft purple
    "danger": "#ff5555",    # Soft red
    "success": "#50fa7b",   # Soft green

    # Text styles
    "title": "bold #bd93f9",      # Purple for titles
    "subtitle": "italic #8be9fd",  # Cyan for subtitles
    "highlight": "#f1fa8c",       # Soft yellow for highlights
    "muted": "dim #6272a4",      # Muted text

    # Entity types
    "user": "#8be9fd",      # Cyan for users
    "group": "#50fa7b",     # Green for groups
    "channel": "#bd93f9",   # Purple for channels
    "unread": "#ff5555",    # Red for unread

    # UI elements
    "border": "#6272a4",     # Soft blue-gray for borders
    "header": "bold #f8f8f2",  # White for headers
    "accent": "#ffb86c",     # Soft orange for accents
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
        self.live = None  # Live display for updating the table in place

    def display_logo(self):
        """Display the ChatShift logo - elegant and minimal"""
        # Clear the screen for a clean start
        os.system('cls' if os.name == 'nt' else 'clear')

        # Create a minimal, elegant logo
        logo = pyfiglet.figlet_format("ChatShift", font="small")

        # Create a layout for the header
        layout = Layout()
        layout.split_column(
            Layout(name="logo"),
            Layout(name="info")
        )

        # Add the logo with gradient effect
        logo_text = Text()
        lines = logo.split('\n')
        for line in lines:
            logo_text.append(line, style="gradient('#8be9fd', '#bd93f9')")
            logo_text.append('\n')

        # Create the logo panel
        logo_panel = Panel(
            Align.center(logo_text),
            box=MINIMAL,
            border_style="border",
            padding=(0, 2)
        )

        # Create the info panel
        info_panel = Panel(
            Group(
                Align.center(Text("v0.4.0", style="subtitle")),
                Align.center(
                    Text("Telegram to WhatsApp Chat Exporter", style="muted")),
                Align.center(Text("Developed by mosaddiX", style="muted"))
            ),
            box=MINIMAL,
            border_style="border",
            padding=(0, 2)
        )

        # Add panels to layout
        layout["logo"].update(logo_panel)
        layout["info"].update(info_panel)

        # Display the layout
        console.print(layout)

        # Add some space
        console.print("")

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

    async def get_dialogs(self, is_refresh=False):
        """Get all dialogs (chats)"""
        try:
            # If refreshing, use a more subtle status indicator
            if is_refresh:
                # Pause the live display to show the status
                if self.live:
                    self.live.stop()

                with console.status("[info]Updating chat list...[/info]", spinner="dots") as status:
                    # Get dialogs
                    self.dialogs = await self.client.get_dialogs()
                    status.update(
                        f"[success]Updated! Found {len(self.dialogs)} chats[/success]")
                    time.sleep(0.3)

                # Update the live display with new data
                if self.live:
                    # Update the content
                    self.live.update(self.create_dialogs_display())
                    # Restart the live display
                    self.live.start()
            else:
                # First time loading - show a more prominent status
                # Create a panel for the dialog fetching process
                fetch_panel = Panel(
                    "[bold]Fetching Your Chats[/bold]\n\n"
                    "Retrieving your Telegram conversations...",
                    title="Chats",
                    border_style="border",
                    box=MINIMAL
                )
                console.print(fetch_panel)

                with console.status("[info]Retrieving chats from Telegram...[/info]", spinner="dots") as status:
                    self.dialogs = await self.client.get_dialogs()
                    status.update(
                        f"[success]Found {len(self.dialogs)} chats![/success]")
                    time.sleep(0.5)

            return True
        except Exception as e:
            console.print(
                f"[danger]Error fetching chats:[/danger] {str(e)}")
            return False

    def create_dialogs_table(self):
        """Create a table for the dialogs"""
        # Create a premium-looking table for the dialogs
        table = Table(
            title="Your Telegram Chats",
            box=MINIMAL,
            border_style="border",
            header_style="header",
            # Alternating row styles for better readability
            row_styles=["none", "dim"],
            title_style="title",
            expand=True,
            padding=(0, 1),
            min_width=80
        )

        # Add columns with elegant styling
        table.add_column("ID", justify="center", style="muted", width=4)
        table.add_column("Type", justify="center", width=10)
        table.add_column("Name", width=40)
        table.add_column("Unread", justify="center", width=8)

        # Add rows for each dialog
        for i, dialog in enumerate(self.dialogs, 1):
            entity = dialog.entity

            # Determine entity type and style - using minimal icons for a cleaner look
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

            # Add row to table with elegant styling
            table.add_row(
                str(i),
                f"[{type_style}]{entity_type}[/{type_style}]",
                dialog.name,
                unread
            )

        return table

    def create_help_text(self):
        """Create help text for the dialog selection"""
        help_text = Text()
        help_text.append("\n")
        help_text.append("Enter a ", style="muted")
        help_text.append("number", style="accent")
        help_text.append(" to select a chat, ", style="muted")
        help_text.append("r", style="accent")
        help_text.append(" to refresh, or ", style="muted")
        help_text.append("q", style="accent")
        help_text.append(" to quit", style="muted")
        return Align.center(help_text)

    def create_dialogs_display(self):
        """Create the complete dialogs display with table and help text"""
        # Create a panel to wrap the table
        panel = Panel(
            self.create_dialogs_table(),
            title="[title]Chats[/title]",
            border_style="border",
            box=MINIMAL,
            padding=(0, 1)
        )

        # Create a group with the panel and help text
        return Group(panel, self.create_help_text())

    def display_dialogs(self):
        """Display all dialogs in a numbered list with live updating"""
        # Create the display
        display = self.create_dialogs_display()

        # Create a Live display for updating in place
        self.live = Live(display, console=console, refresh_per_second=4)

        # Start the live display
        self.live.start()

        # We'll keep the live display running in the background for updates

    def select_dialog(self):
        """Let the user select a dialog"""
        # Stop the live display before getting input
        if self.live:
            self.live.stop()

        while True:
            try:
                # Styled input prompt with minimal design
                choice = console.input("\n[bold]>[/bold] ")

                if choice.lower() == 'q':
                    console.print("[muted]Exiting...[/muted]")
                    return None
                elif choice.lower() == 'r':
                    # Update the table in place instead of printing a new one
                    console.print("[muted]Refreshing chats...[/muted]")
                    return 'refresh'

                choice = int(choice)
                if 1 <= choice <= len(self.dialogs):
                    selected = self.dialogs[choice - 1]
                    # Show selection with elegant styling
                    selection_panel = Panel(
                        f"Selected: [accent]{selected.name}[/accent]",
                        box=MINIMAL,
                        border_style="border",
                        padding=(0, 1)
                    )
                    console.print(selection_panel)
                    return selected
                else:
                    console.print(
                        f"[warning]Please enter a number between 1 and {len(self.dialogs)}.[/warning]")
                    # Restart the live display if we're continuing
                    if self.live:
                        self.live.start()
            except ValueError:
                console.print(
                    "[warning]Please enter a valid number.[/warning]")
                # Restart the live display if we're continuing
                if self.live:
                    self.live.start()

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
                "\n[danger]Authentication failed. Exiting...[/danger]")
            return

        # Main loop
        is_first_run = True
        while True:
            # Get dialogs - pass is_refresh flag to update in place when refreshing
            if is_first_run:
                if not await self.get_dialogs(is_refresh=False):
                    console.print(
                        "\n[danger]Failed to fetch chats. Exiting...[/danger]")
                    break
                # Display dialogs on first run only
                self.display_dialogs()
                is_first_run = False

            # Select dialog
            selected_dialog = self.select_dialog()

            if selected_dialog is None:
                # User wants to quit
                break
            elif selected_dialog == 'refresh':
                # User wants to refresh - update in place
                if not await self.get_dialogs(is_refresh=True):
                    console.print(
                        "\n[danger]Failed to refresh chats. Exiting...[/danger]")
                    break
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

        # Stop the live display if it's running
        if self.live:
            self.live.stop()

        # Disconnect from Telegram
        if self.client:
            with console.status("[info]Disconnecting from Telegram...[/info]", spinner="dots") as status:
                await self.client.disconnect()
                time.sleep(0.5)
                status.update("[success]Disconnected![/success]")
                time.sleep(0.5)

        # Farewell message
        farewell_panel = Panel(
            "[success]Thank you for using ChatShift![/success]\n\n"
            "[subtitle]Your chats have been exported successfully.[/subtitle]",
            title="Goodbye",
            border_style="border",
            box=MINIMAL,
            padding=(1, 2)
        )
        console.print(farewell_panel)


async def main():
    """Main function"""
    cli = ChatShiftCLI()
    await cli.run()

if __name__ == "__main__":
    # Run the CLI
    asyncio.run(main())
