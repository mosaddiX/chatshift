#!/usr/bin/env python3
"""
ChatShift - Export Telegram chats to various text formats

ChatShift allows you to export Telegram chats to multiple formats including
WhatsApp, Telegram, Discord, and custom formats. It supports multiple chat
export, statistics generation, and media downloading with filtering options.

This is the main entry point for the ChatShift application.
Run this file to start the application.

Author: mosaddiX
Version: 1.0.0
"""

import os
import sys
import time
import asyncio
import logging
import datetime
import mimetypes
from pathlib import Path
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import User, Chat, Channel, Dialog
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, MessageMediaWebPage

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
from rich.status import Status
from contextlib import asynccontextmanager

# Additional styling
import colorama
from colorama import Fore, Back, Style as ColoramaStyle
from termcolor import colored
import pyfiglet

# Initialize colorama
colorama.init(autoreset=True)

# Configure logging - disable Telethon logs to keep the interface clean
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Specifically silence Telethon's network logs
logging.getLogger('telethon').setLevel(logging.ERROR)  # Only show errors
logging.getLogger('telethon.network').setLevel(logging.ERROR)

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

# Format templates
FORMAT_TEMPLATES = {
    'whatsapp': {
        'name': 'WhatsApp',
        'description': 'Standard WhatsApp format',
        'date_format': '%d/%m/%y, %H:%M',
        'message_format': '{date_str} - {sender_name}: {content}{edited_suffix}',
        'header_format': '{date_str} - Chat export from {chat_title}',
        'include_header': True,
        'media_placeholder': '<Media omitted>',
        'unknown_message_placeholder': '<Message>',
        'error_placeholder': '<Message format error>',
        'edited_suffix': ' (edited)'
    },
    'telegram': {
        'name': 'Telegram',
        'description': 'Telegram-style format',
        'date_format': '%Y-%m-%d %H:%M:%S',
        'message_format': '[{date_str}] {sender_name}: {content}{edited_suffix}',
        'header_format': '--- Telegram Chat Export ---\nChat: {chat_title}\nExport date: {date_str}\n---',
        'include_header': True,
        'media_placeholder': '[Media]',
        'unknown_message_placeholder': '[Message]',
        'error_placeholder': '[Error: Message could not be formatted]',
        'edited_suffix': ' (edited)'
    },
    'discord': {
        'name': 'Discord',
        'description': 'Discord-style format',
        'date_format': '%Y-%m-%d %H:%M',
        'message_format': '{sender_name} [{date_str}]: {content}{edited_suffix}',
        'header_format': '# {chat_title} - Export Date: {date_str}',
        'include_header': True,
        'media_placeholder': '[attachment]',
        'unknown_message_placeholder': '[message]',
        'error_placeholder': '[error: could not format message]',
        'edited_suffix': ' (edited)'
    },
    'simple': {
        'name': 'Simple',
        'description': 'Simple, clean format',
        'date_format': '%Y-%m-%d %H:%M',
        'message_format': '{sender_name} ({date_str}): {content}{edited_suffix}',
        'header_format': '=== {chat_title} ===\nExported on {date_str}\n',
        'include_header': True,
        'media_placeholder': '[media]',
        'unknown_message_placeholder': '[message]',
        'error_placeholder': '[error]',
        'edited_suffix': ' (edited)'
    },
    'no_header': {
        'name': 'No Header',
        'description': 'Format without any header',
        'date_format': '%d/%m/%y, %H:%M',
        'message_format': '{date_str} - {sender_name}: {content}{edited_suffix}',
        'header_format': '',  # Empty header
        'include_header': False,  # Don't include header
        'media_placeholder': '<Media>',
        'unknown_message_placeholder': '<Message>',
        'error_placeholder': '<Error>',
        'edited_suffix': ' (edited)'
    },
    'custom': {
        'name': 'Custom',
        'description': 'User-defined custom format',
        'date_format': '%d/%m/%y, %H:%M',  # Default, will be overridden by user input
        # Default, will be overridden by user input
        'message_format': '{date_str} - {sender_name}: {content}{edited_suffix}',
        # Default, will be overridden by user input
        'header_format': '--- {chat_title} ---\nExport date: {date_str}',
        'include_header': True,  # Default, will be overridden by user input
        'media_placeholder': '<Media>',  # Default, will be overridden by user input
        # Default, will be overridden by user input
        'unknown_message_placeholder': '<Message>',
        'error_placeholder': '<Error>',  # Default, will be overridden by user input
        # Default, will be overridden by user input
        'edited_suffix': ' (edited)'
    }
}


@asynccontextmanager
async def status_context(message):
    """Async context manager for status updates"""
    status = Status(message, console=console)
    status.start()
    try:
        yield status
    finally:
        status.stop()


class ChatShiftCLI:
    """Elegant CLI for ChatShift"""

    def __init__(self):
        """Initialize the CLI"""
        self.client = None
        self.dialogs = []
        self.spinner_chars = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']

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
                Align.center(Text("v0.5.0", style="subtitle")),
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
                # Clear the console output
                console.clear()

                # Show the logo again for consistency
                self.display_logo()

                # Show a status message
                with console.status("[info]Updating chat list...[/info]", spinner="dots") as status:
                    # Get dialogs
                    self.dialogs = await self.client.get_dialogs()
                    status.update(
                        f"[success]Updated! Found {len(self.dialogs)} chats[/success]")
                    time.sleep(0.3)

                # Display the updated dialogs table
                console.print(self.create_dialogs_display())
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
        """Display all dialogs in a numbered list"""
        # Create and display the dialogs
        display = self.create_dialogs_display()
        console.print(display)

    def select_dialog(self, multiple=False):
        """Let the user select a dialog or multiple dialogs"""
        if not multiple:
            # Single dialog selection
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
                except ValueError:
                    console.print(
                        "[warning]Please enter a valid number.[/warning]")
        else:
            # Multiple dialog selection
            selected_dialogs = []
            selected_indices = set()

            console.print("\n[info]Multiple chat selection mode:[/info]")
            console.print("- Enter a number to select a chat")
            console.print("- Enter 'd' when you're done selecting")
            console.print("- Enter 'v' to view all selected chats")
            console.print("- Enter 'r' to refresh the chat list")
            console.print("- Enter 'q' to quit")

            while True:
                try:
                    # We don't show the full list after each selection to avoid duplication
                    # Instead, we'll just show the count in the prompt

                    # Styled input prompt with selected chat count
                    prompt = "\n[bold]>[/bold] "
                    if selected_dialogs:
                        prompt = f"\n[bold]Selected: [accent]{len(selected_dialogs)}[/accent] >[/bold] "
                    choice = console.input(prompt)

                    if choice.lower() == 'q':
                        console.print("[muted]Exiting...[/muted]")
                        return None
                    elif choice.lower() == 'r':
                        console.print("[muted]Refreshing chats...[/muted]")
                        return 'refresh'
                    elif choice.lower() == 'v':
                        # Show all selected chats in a table
                        if selected_dialogs:
                            table = Table(
                                title=f"All Selected Chats ({len(selected_dialogs)})")
                            table.add_column("#", style="dim")
                            table.add_column("Chat Name", style="cyan")

                            for i, dialog in enumerate(selected_dialogs, 1):
                                table.add_row(str(i), dialog.name)

                            console.print(table)
                        continue
                    elif choice.lower() == 'd':
                        if selected_dialogs:
                            # Show final selection with elegant styling
                            selection_panel = Panel(
                                f"Selected [accent]{len(selected_dialogs)}[/accent] chats",
                                box=MINIMAL,
                                border_style="border",
                                padding=(0, 1)
                            )
                            console.print(selection_panel)
                            return selected_dialogs
                        else:
                            console.print(
                                "[warning]Please select at least one chat.[/warning]")
                            continue

                    choice = int(choice)
                    if 1 <= choice <= len(self.dialogs):
                        if choice - 1 in selected_indices:
                            console.print(
                                "[warning]This chat is already selected.[/warning]")
                        else:
                            selected = self.dialogs[choice - 1]
                            selected_dialogs.append(selected)
                            selected_indices.add(choice - 1)

                            # Show a confirmation for the newly added chat only
                            console.print(
                                f"[success]Added:[/success] [accent]{selected.name}[/accent]")

                            # Remind about 'v' command if we have multiple chats
                            if len(selected_dialogs) > 1 and len(selected_dialogs) % 5 == 0:
                                console.print(
                                    "[dim]Remember: Enter 'v' to view all selected chats[/dim]")
                    else:
                        console.print(
                            f"[warning]Please enter a number between 1 and {len(self.dialogs)}.[/warning]")
                except ValueError:
                    if choice.lower() not in ['q', 'r', 'd']:
                        console.print(
                            "[warning]Please enter a valid number or command.[/warning]")

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

        # Ask if user wants to filter by date range
        use_date_filter = console.input(
            "\n[bold]Filter by date range?[/bold] (y/n, default: n): ").lower() == 'y'

        start_date = None
        end_date = None

        # Ask if user wants to filter media types
        use_media_filter = console.input(
            "\n[bold]Filter media types?[/bold] (y/n, default: n): ").lower() == 'y'

        # Default to including all media types
        include_photos = True
        include_videos = True
        include_documents = True
        include_audio = True
        include_stickers = True
        include_voice = True

        # No message type filtering - all message types are included by default

        # If user wants to filter media types, ask for each type
        if use_media_filter:
            # Create a panel for media options
            media_panel = Panel(
                "[bold]Media Type Filtering[/bold]\n\n"
                "Select which media types to include in the export.",
                title="Media Options",
                border_style="cyan",
                box=ROUNDED
            )
            console.print(media_panel)

            # Ask for each media type
            include_photos = console.input(
                "\n[bold]Include photos?[/bold] (y/n, default: y): ").lower() != 'n'
            include_videos = console.input(
                "[bold]Include videos?[/bold] (y/n, default: y): ").lower() != 'n'
            include_documents = console.input(
                "[bold]Include documents?[/bold] (y/n, default: y): ").lower() != 'n'
            include_audio = console.input(
                "[bold]Include audio files?[/bold] (y/n, default: y): ").lower() != 'n'
            include_stickers = console.input(
                "[bold]Include stickers?[/bold] (y/n, default: y): ").lower() != 'n'
            include_voice = console.input(
                "[bold]Include voice messages?[/bold] (y/n, default: y): ").lower() != 'n'

            # Show summary of selected options
            console.print("\n[bold]Media types to include:[/bold]")
            console.print(
                f"[dim]→ Photos:[/dim] [cyan]{'Yes' if include_photos else 'No'}[/cyan]")
            console.print(
                f"[dim]→ Videos:[/dim] [cyan]{'Yes' if include_videos else 'No'}[/cyan]")
            console.print(
                f"[dim]→ Documents:[/dim] [cyan]{'Yes' if include_documents else 'No'}[/cyan]")
            console.print(
                f"[dim]→ Audio:[/dim] [cyan]{'Yes' if include_audio else 'No'}[/cyan]")
            console.print(
                f"[dim]→ Stickers:[/dim] [cyan]{'Yes' if include_stickers else 'No'}[/cyan]")
            console.print(
                f"[dim]→ Voice messages:[/dim] [cyan]{'Yes' if include_voice else 'No'}[/cyan]")

        # No message type filtering UI - all message types are included by default

        if use_date_filter:
            # Get start date with validation
            while True:
                try:
                    start_date_input = console.input(
                        "[bold]Start date[/bold] [dim](YYYY-MM-DD, leave empty for no start date):[/dim] ")

                    if not start_date_input:
                        console.print("[dim]→ No start date filter[/dim]")
                        break

                    # Parse and validate the date
                    start_date = datetime.datetime.strptime(
                        start_date_input, "%Y-%m-%d")
                    # Make timezone-aware by setting to UTC
                    start_date = start_date.replace(
                        tzinfo=datetime.timezone.utc)
                    console.print(
                        f"[dim]→ Start date:[/dim] [cyan]{start_date.strftime('%Y-%m-%d')}[/cyan]")
                    break
                except ValueError:
                    console.print(
                        "[bold yellow]Please enter a valid date in YYYY-MM-DD format.[/bold yellow]")

            # Get end date with validation
            while True:
                try:
                    end_date_input = console.input(
                        "[bold]End date[/bold] [dim](YYYY-MM-DD, leave empty for no end date):[/dim] ")

                    if not end_date_input:
                        console.print("[dim]→ No end date filter[/dim]")
                        break

                    # Parse and validate the date
                    end_date = datetime.datetime.strptime(
                        end_date_input, "%Y-%m-%d")

                    # Add one day to end date to include the entire day
                    end_date = end_date + datetime.timedelta(days=1)

                    # Make timezone-aware by setting to UTC
                    end_date = end_date.replace(tzinfo=datetime.timezone.utc)

                    console.print(
                        f"[dim]→ End date:[/dim] [cyan]{end_date_input}[/cyan]")

                    # Validate date range if both dates are provided
                    if start_date and end_date and start_date > end_date:
                        console.print(
                            "[bold yellow]End date must be after start date.[/bold yellow]")
                        end_date = None
                        continue

                    break
                except ValueError:
                    console.print(
                        "[bold yellow]Please enter a valid date in YYYY-MM-DD format.[/bold yellow]")

        # Ask for file naming options
        use_custom_naming = console.input(
            "\n[bold]Use custom file naming options?[/bold] (y/n, default: n): ").lower() == 'y'

        file_pattern = ""
        file_extension = ""
        custom_name_info = ""

        if use_custom_naming:
            # Create a panel for file naming options
            file_panel = Panel(
                "[bold]File Naming Options[/bold]\n\n"
                "Customize how your exported file will be named.",
                title="File Options",
                border_style="cyan",
                box=ROUNDED
            )
            console.print(file_panel)

            # Ask for file name pattern
            console.print("\n[bold]Available placeholders:[/bold]")
            console.print("[dim]{chat_name}[/dim] - Name of the chat")
            console.print("[dim]{date}[/dim] - Current date (YYYY-MM-DD)")
            console.print("[dim]{time}[/dim] - Current time (HHMM)")

            # Default pattern
            default_pattern = "{chat_name}_{date}"

            # Get custom pattern
            file_pattern = console.input(
                f"\n[bold]File name pattern[/bold] [dim](default: {default_pattern}):[/dim] ")

            if not file_pattern:
                file_pattern = default_pattern

            # Get file extension
            extension_input = console.input(
                "\n[bold]File extension[/bold] [dim](default: txt):[/dim] ")

            if not extension_input:
                file_extension = ".txt"
            elif not extension_input.startswith("."):
                file_extension = "." + extension_input
            else:
                file_extension = extension_input

            # Generate output file name based on pattern
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            current_time = datetime.datetime.now().strftime("%H%M")

            # We'll replace {chat_name} later when we have the selected dialog
            output_file = file_pattern.replace(
                "{date}", current_date).replace("{time}", current_time)

            # Store the pattern for later use
            custom_name_info = file_pattern + file_extension

            # For now, use a temporary name - we'll update it when we know the chat name
            output_file = output_file.replace(
                "{chat_name}", "CHAT") + file_extension

            console.print(
                f"[dim]→ File name pattern:[/dim] [cyan]{custom_name_info}[/cyan]")
        else:
            # Get output file with styled input (traditional way)
            output_file = console.input(
                f"\n[bold]Output file[/bold] [dim](default: {DEFAULT_OUTPUT_FILE}):[/dim] ")

            if not output_file:
                output_file = DEFAULT_OUTPUT_FILE

        # Show confirmation of the output file
        console.print(f"[dim]→ Will save to[/dim] [cyan]{output_file}[/cyan]")

        # Ask for format customization
        format_panel = Panel(
            "[bold]Format Customization[/bold]\n\n"
            "Select the format for your exported messages.",
            title="Format Options",
            border_style="cyan",
            box=ROUNDED
        )
        console.print(format_panel)

        # Display available format templates
        console.print("[bold]Available formats:[/bold]")
        for i, (key, template) in enumerate(FORMAT_TEMPLATES.items(), 1):
            console.print(
                f"[dim]{i}.[/dim] [cyan]{template['name']}[/cyan] - {template['description']}")

        # Ask user to select a format
        format_choice = console.input(
            "\n[bold]Select a format (1-{}):[/bold] ".format(len(FORMAT_TEMPLATES)))

        # Default to WhatsApp format if invalid choice
        try:
            format_index = int(format_choice) - 1
            if 0 <= format_index < len(FORMAT_TEMPLATES):
                format_key = list(FORMAT_TEMPLATES.keys())[format_index]
            else:
                format_key = 'whatsapp'
                console.print(
                    "[warning]Invalid choice. Using WhatsApp format.[/warning]")
        except ValueError:
            format_key = 'whatsapp'
            console.print(
                "[warning]Invalid choice. Using WhatsApp format.[/warning]")

        # Get the selected format template
        format_template = FORMAT_TEMPLATES[format_key]
        console.print(
            f"[dim]→ Selected format:[/dim] [cyan]{format_template['name']}[/cyan]")

        # If custom format is selected, allow customization
        if format_key == 'custom':
            console.print("\n[bold]Custom Format Options:[/bold]")

            # Date format
            date_format = console.input(
                f"[bold]Date format:[/bold] (default: {format_template['date_format']}): ") or format_template['date_format']
            format_template['date_format'] = date_format

            # Message format
            message_format = console.input(
                f"[bold]Message format:[/bold] (default: {format_template['message_format']}): ") or format_template['message_format']
            format_template['message_format'] = message_format

            # Header format
            header_format = console.input(
                f"[bold]Header format:[/bold] (default: {format_template['header_format']}): ") or format_template['header_format']
            format_template['header_format'] = header_format

            # Include header option
            include_header_choice = console.input(
                f"[bold]Include header?[/bold] (y/n, default: {'y' if format_template['include_header'] else 'n'}): ")
            if include_header_choice.lower() in ['y', 'yes', 'n', 'no']:
                format_template['include_header'] = include_header_choice.lower() in [
                    'y', 'yes']

            # Media placeholder
            media_placeholder = console.input(
                f"[bold]Media placeholder:[/bold] (default: {format_template['media_placeholder']}): ") or format_template['media_placeholder']
            format_template['media_placeholder'] = media_placeholder

            # Unknown message placeholder
            unknown_message_placeholder = console.input(
                f"[bold]Unknown message placeholder:[/bold] (default: {format_template['unknown_message_placeholder']}): ") or format_template['unknown_message_placeholder']
            format_template['unknown_message_placeholder'] = unknown_message_placeholder

            # Error placeholder
            error_placeholder = console.input(
                f"[bold]Error placeholder:[/bold] (default: {format_template['error_placeholder']}): ") or format_template['error_placeholder']
            format_template['error_placeholder'] = error_placeholder

            # Edited suffix
            edited_suffix = console.input(
                f"[bold]Edited suffix:[/bold] (default: {format_template['edited_suffix']}): ") or format_template['edited_suffix']
            format_template['edited_suffix'] = edited_suffix

            console.print("[success]Custom format configured![/success]")

        return {
            'limit': limit,
            'output_file': output_file,
            'start_date': start_date,
            'end_date': end_date,
            'include_photos': include_photos,
            'include_videos': include_videos,
            'include_documents': include_documents,
            'include_audio': include_audio,
            'include_stickers': include_stickers,
            'include_voice': include_voice,
            'use_custom_naming': use_custom_naming,
            'file_pattern': file_pattern,
            'file_extension': file_extension,
            'custom_name_info': custom_name_info,
            'format_template': format_template
        }

    async def generate_export_statistics(self, messages, dialog, output_file=None):
        """Generate statistics about the exported chat"""
        if not messages:
            console.print(
                "[warning]No messages to generate statistics for.[/warning]")
            return None

        # Count message types
        total_messages = len(messages)
        text_messages = sum(1 for m in messages if hasattr(
            m, 'text') and m.text and not m.media)
        media_messages = sum(
            1 for m in messages if hasattr(m, 'media') and m.media)
        service_messages = sum(
            1 for m in messages if hasattr(m, 'action') and m.action)
        edited_messages = sum(1 for m in messages if hasattr(
            m, 'edit_date') and m.edit_date)

        # Count media types
        photos = sum(1 for m in messages if hasattr(m, 'media')
                     and m.media and hasattr(m.media, 'photo') and m.media.photo)
        videos = sum(1 for m in messages if hasattr(m, 'media') and m.media and hasattr(m.media, 'document')
                     and m.media.document and m.media.document.mime_type and m.media.document.mime_type.startswith('video/'))
        documents = sum(1 for m in messages if hasattr(m, 'media') and m.media and hasattr(m.media, 'document') and m.media.document and (
            not m.media.document.mime_type or not (m.media.document.mime_type.startswith('video/') or m.media.document.mime_type.startswith('audio/'))))
        audio = sum(1 for m in messages if hasattr(m, 'media') and m.media and hasattr(m.media, 'document')
                    and m.media.document and m.media.document.mime_type and m.media.document.mime_type.startswith('audio/'))

        # Count messages by sender
        senders = {}
        for message in messages:
            if hasattr(message, 'sender') and message.sender:
                sender_name = getattr(message.sender, 'first_name', getattr(
                    message.sender, 'title', 'Unknown'))
                if hasattr(message.sender, 'last_name') and message.sender.last_name:
                    sender_name += f" {message.sender.last_name}"

                senders[sender_name] = senders.get(sender_name, 0) + 1

        # Get date range
        if messages:
            first_date = min(m.date for m in messages)
            last_date = max(m.date for m in messages)
            date_range = (last_date - first_date).days + 1
            messages_per_day = total_messages / \
                date_range if date_range > 0 else total_messages
        else:
            first_date = last_date = datetime.datetime.now()
            date_range = 0
            messages_per_day = 0

        # Create statistics table
        table = Table(title=f"Chat Statistics: {dialog.name}")
        table.add_column("Statistic", style="cyan")
        table.add_column("Value", style="green")

        # Add rows
        table.add_row("Total Messages", str(total_messages))
        table.add_row(
            "Text Messages", f"{text_messages} ({text_messages/total_messages*100:.1f}%)")
        table.add_row(
            "Media Messages", f"{media_messages} ({media_messages/total_messages*100:.1f}%)")
        table.add_row("Service Messages",
                      f"{service_messages} ({service_messages/total_messages*100:.1f}%)")
        table.add_row(
            "Edited Messages", f"{edited_messages} ({edited_messages/total_messages*100:.1f}%)")
        table.add_row("Photos", str(photos))
        table.add_row("Videos", str(videos))
        table.add_row("Documents", str(documents))
        table.add_row("Audio Files", str(audio))
        table.add_row(
            "Date Range", f"{first_date.strftime('%Y-%m-%d')} to {last_date.strftime('%Y-%m-%d')} ({date_range} days)")
        table.add_row("Messages per Day", f"{messages_per_day:.1f}")

        # Display the table
        console.print(table)

        # Create top senders table
        if senders:
            top_senders = sorted(senders.items(), key=lambda x: x[1], reverse=True)[
                :10]  # Top 10 senders

            senders_table = Table(title="Top Message Senders")
            senders_table.add_column("Sender", style="cyan")
            senders_table.add_column("Messages", style="green")
            senders_table.add_column("Percentage", style="yellow")

            for sender, count in top_senders:
                senders_table.add_row(sender, str(
                    count), f"{count/total_messages*100:.1f}%")

            console.print(senders_table)

        # Export statistics to file if requested
        if output_file:
            stats_file = os.path.splitext(output_file)[0] + "_stats.txt"

            with open(stats_file, 'w', encoding='utf-8') as f:
                f.write(f"Chat Statistics: {dialog.name}\n")
                f.write(
                    f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

                f.write(f"Total Messages: {total_messages}\n")
                f.write(
                    f"Text Messages: {text_messages} ({text_messages/total_messages*100:.1f}%)\n")
                f.write(
                    f"Media Messages: {media_messages} ({media_messages/total_messages*100:.1f}%)\n")
                f.write(
                    f"Service Messages: {service_messages} ({service_messages/total_messages*100:.1f}%)\n")
                f.write(
                    f"Edited Messages: {edited_messages} ({edited_messages/total_messages*100:.1f}%)\n\n")

                f.write(f"Photos: {photos}\n")
                f.write(f"Videos: {videos}\n")
                f.write(f"Documents: {documents}\n")
                f.write(f"Audio Files: {audio}\n\n")

                f.write(
                    f"Date Range: {first_date.strftime('%Y-%m-%d')} to {last_date.strftime('%Y-%m-%d')} ({date_range} days)\n")
                f.write(f"Messages per Day: {messages_per_day:.1f}\n\n")

                f.write("Top Message Senders:\n")
                for sender, count in top_senders:
                    f.write(
                        f"{sender}: {count} ({count/total_messages*100:.1f}%)\n")

            console.print(
                f"\n[success]Statistics exported to:[/success] [cyan]{stats_file}[/cyan]")

        return {
            'total_messages': total_messages,
            'text_messages': text_messages,
            'media_messages': media_messages,
            'service_messages': service_messages,
            'edited_messages': edited_messages,
            'photos': photos,
            'videos': videos,
            'documents': documents,
            'audio': audio,
            'first_date': first_date,
            'last_date': last_date,
            'date_range': date_range,
            'messages_per_day': messages_per_day,
            'senders': senders
        }

    async def export_chat(self, dialog, limit, output_file, start_date=None, end_date=None,
                          include_photos=True, include_videos=True, include_documents=True,
                          include_audio=True, include_stickers=True, include_voice=True,
                          format_template=None, custom_name_info=None, generate_stats=False):
        """Export a chat to WhatsApp format"""
        # Create an export panel with details
        export_details = [
            f"[bold]Exporting Chat:[/bold] [cyan]{dialog.name}[/cyan]",
            f"[bold]Message Limit:[/bold] [cyan]{limit if limit > 0 else 'All'}[/cyan]",
            f"[bold]Output File:[/bold] [cyan]{output_file}[/cyan]"
        ]

        # Add date range information if provided
        if start_date:
            export_details.append(
                f"[bold]Start Date:[/bold] [cyan]{start_date.strftime('%Y-%m-%d')}[/cyan]")
        if end_date:
            export_details.append(
                f"[bold]End Date:[/bold] [cyan]{(end_date - datetime.timedelta(days=1)).strftime('%Y-%m-%d')}[/cyan]")

        # Add media filtering information
        media_types = []
        if not (include_photos and include_videos and include_documents and include_audio and include_stickers and include_voice):
            if include_photos:
                media_types.append("Photos")
            if include_videos:
                media_types.append("Videos")
            if include_documents:
                media_types.append("Documents")
            if include_audio:
                media_types.append("Audio")
            if include_stickers:
                media_types.append("Stickers")
            if include_voice:
                media_types.append("Voice")

            if media_types:
                export_details.append(
                    f"[bold]Media Types:[/bold] [cyan]{', '.join(media_types)}[/cyan]")
            else:
                export_details.append(
                    f"[bold]Media Types:[/bold] [warning]None (text only)[/warning]")
        else:
            export_details.append(
                f"[bold]Media Types:[/bold] [cyan]All[/cyan]")

        # No message type filtering information - all message types are included

        export_panel = Panel(
            "\n".join(export_details),
            title="Export Details",
            border_style="cyan",
            box=ROUNDED
        )
        console.print(export_panel)

        # Set a reasonable default if limit is 0
        actual_limit = 5000 if limit == 0 else limit

        try:
            # Create a progress display
            async with status_context("[bold cyan]Preparing to download messages...[/bold cyan]") as status:
                # Initialize counters
                messages = []
                message_count = 0
                batch_size = 100  # Process messages in batches for better performance

                # Show progress message
                status.update("[bold cyan]Downloading messages...[/bold cyan]")

                # Define filter function for better performance
                def message_filter(msg):
                    # Skip messages without date
                    if not msg or not hasattr(msg, 'date') or not msg.date:
                        return False

                    # Check date filters
                    if start_date and msg.date < start_date:
                        return False
                    if end_date and msg.date > end_date:
                        return False

                    # Check media type filters
                    if hasattr(msg, 'media') and msg.media:
                        # Skip photos if not included
                        if not include_photos and isinstance(msg.media, MessageMediaPhoto):
                            return False

                        # Skip videos if not included
                        if not include_videos and hasattr(msg.media, 'document') and \
                           hasattr(msg.media.document, 'mime_type') and \
                           msg.media.document.mime_type and \
                           msg.media.document.mime_type.startswith('video/'):
                            return False

                        # Skip documents if not included
                        if not include_documents and hasattr(msg.media, 'document') and \
                           not (hasattr(msg.media.document, 'mime_type') and
                                msg.media.document.mime_type and
                                (msg.media.document.mime_type.startswith('video/') or
                                 msg.media.document.mime_type.startswith('audio/'))):
                            return False

                        # Skip audio if not included
                        if not include_audio and hasattr(msg.media, 'document') and \
                           hasattr(msg.media.document, 'mime_type') and \
                           msg.media.document.mime_type and \
                           msg.media.document.mime_type.startswith('audio/') and \
                           not msg.media.document.mime_type.endswith('ogg'):
                            return False

                        # Skip stickers if not included
                        if not include_stickers and hasattr(msg, 'sticker') and msg.sticker:
                            return False

                        # Skip voice messages if not included
                        if not include_voice and hasattr(msg.media, 'document') and \
                           hasattr(msg.media.document, 'mime_type') and \
                           msg.media.document.mime_type and \
                           msg.media.document.mime_type.endswith('ogg'):
                            return False

                    # Message passed all filters
                    return True

                # Process messages in batches for better performance
                offset_id = 0
                while True:
                    # Get a batch of messages
                    batch = await self.client.get_messages(dialog.entity, limit=batch_size, offset_id=offset_id)
                    if not batch:
                        break

                    # Update offset for next batch
                    offset_id = batch[-1].id

                    # Filter and add messages
                    filtered_batch = [
                        msg for msg in batch if message_filter(msg)]
                    messages.extend(filtered_batch)

                    # Update progress
                    message_count += len(batch)
                    status.update(
                        f"[bold cyan]Downloaded {message_count} messages...[/bold cyan]")

                    # Check if we've reached the limit
                    if actual_limit > 0 and len(messages) >= actual_limit:
                        # Trim to exact limit
                        messages = messages[:actual_limit]
                        break

                    # Check if we've processed enough messages
                    if actual_limit > 0 and message_count >= actual_limit * 2:  # Safety check
                        break

                # Show completion message
                status.update(
                    f"[bold green]Downloaded {message_count} messages![/bold green]")
                time.sleep(0.5)

                # No debug message type counts - removed with message type filtering

                # Format messages using the selected template
                status.update("[bold cyan]Formatting messages...[/bold cyan]")
                formatted_messages = await self.format_messages(messages, dialog.name, format_template)
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
            success_details = [
                f"[bold green]✓ Export completed successfully![/bold green]\n",
                f"[bold]Messages Exported:[/bold] [cyan]{len(messages)}[/cyan]",
                f"[bold]Output File:[/bold] [cyan]{output_file}[/cyan]"
            ]

            # Add date range information if provided
            if start_date:
                success_details.append(
                    f"[bold]Start Date:[/bold] [cyan]{start_date.strftime('%Y-%m-%d')}[/cyan]")
            if end_date:
                success_details.append(
                    f"[bold]End Date:[/bold] [cyan]{(end_date - datetime.timedelta(days=1)).strftime('%Y-%m-%d')}[/cyan]")

            # Add media filtering information
            media_types = []
            if not (include_photos and include_videos and include_documents and include_audio and include_stickers and include_voice):
                if include_photos:
                    media_types.append("Photos")
                if include_videos:
                    media_types.append("Videos")
                if include_documents:
                    media_types.append("Documents")
                if include_audio:
                    media_types.append("Audio")
                if include_stickers:
                    media_types.append("Stickers")
                if include_voice:
                    media_types.append("Voice")

                if media_types:
                    success_details.append(
                        f"[bold]Media Types:[/bold] [cyan]{', '.join(media_types)}[/cyan]")
                else:
                    success_details.append(
                        f"[bold]Media Types:[/bold] [warning]None (text only)[/warning]")
            else:
                success_details.append(
                    f"[bold]Media Types:[/bold] [cyan]All[/cyan]")

            # No message type filtering information - all message types are included

            # Add file naming information if custom naming was used
            if custom_name_info:
                success_details.append(
                    f"[bold]File Naming Pattern:[/bold] [cyan]{custom_name_info}[/cyan]")

            success_panel = Panel(
                "\n".join(success_details),
                title="Success",
                border_style="green",
                box=ROUNDED
            )
            console.print(success_panel)

            # Generate statistics if requested
            if generate_stats:
                console.print("\n[bold]Generating chat statistics...[/bold]")
                await self.generate_export_statistics(messages, dialog, output_file)

            # Ask if user wants to generate statistics
            gen_stats = console.input(
                "\n[bold]Do you want to generate chat statistics?[/bold] (y/n): ")
            if gen_stats.lower() == 'y':
                console.print("\n[bold]Generating chat statistics...[/bold]")
                await self.generate_export_statistics(messages, dialog, output_file)

            # Ask if user wants to open the file
            open_file = console.input(
                "\n[bold]Do you want to open the file?[/bold] (y/n): ")
            if open_file.lower() == 'y':
                async with status_context("[bold cyan]Opening file...[/bold cyan]") as status:
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

    def format_date(self, date, format_template):
        """Format date according to the selected template"""
        return date.strftime(format_template['date_format'])

    async def format_message(self, message, chat_title=None, format_template=None):
        """Format a single message according to the selected template"""
        # Use default WhatsApp format if no template is provided
        if not format_template:
            format_template = FORMAT_TEMPLATES['whatsapp']

        # Skip empty messages
        if not message:
            return None

        try:
            # Get message date
            date_str = self.format_date(message.date, format_template)

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
            edited_suffix = format_template['edited_suffix'] if message.edit_date else ""

            # Get message content
            if hasattr(message, 'media') and message.media:
                # Media message
                content = format_template['media_placeholder']
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
                content = format_template['unknown_message_placeholder']
        except Exception:
            content = format_template['error_placeholder']
            edited_suffix = ""

        # Format according to the selected template
        return format_template['message_format'].format(
            date_str=date_str,
            sender_name=sender_name,
            content=content,
            edited_suffix=edited_suffix
        )

    def format_chat_header(self, chat_title, format_template=None):
        """Format chat header according to the selected template"""
        # Use default WhatsApp format if no template is provided
        if not format_template:
            format_template = FORMAT_TEMPLATES['whatsapp']

        today = datetime.datetime.now()
        date_str = self.format_date(today, format_template)

        return format_template['header_format'].format(
            date_str=date_str,
            chat_title=chat_title
        )

    async def format_messages(self, messages, chat_title, format_template=None):
        """Format a list of messages according to the selected template"""
        # Use default WhatsApp format if no template is provided
        if not format_template:
            format_template = FORMAT_TEMPLATES['whatsapp']

        # Initialize the formatted messages list
        formatted_messages = []

        # Add the header if include_header is True
        if format_template.get('include_header', True):
            formatted_messages.append(
                self.format_chat_header(chat_title, format_template))

        # Process messages in reverse order (oldest first, like WhatsApp)
        for message in reversed(messages):
            try:
                formatted = await self.format_message(message, chat_title, format_template)
                if formatted:
                    formatted_messages.append(formatted)
            except Exception as e:
                logger.error(f"Error formatting message: {str(e)}")

        return formatted_messages

    async def run(self):
        """Run the CLI"""
        try:
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
                try:
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

                    # Ask what the user wants to do with this chat
                    action_panel = Panel(
                        "[bold]What would you like to do?[/bold]",
                        title="Action Options",
                        border_style="cyan",
                        box=ROUNDED
                    )
                    console.print(action_panel)

                    console.print(
                        "[dim]1.[/dim] [cyan]Export messages only[/cyan]")
                    console.print(
                        "[dim]2.[/dim] [cyan]Download media only[/cyan]")
                    console.print(
                        "[dim]3.[/dim] [cyan]Export messages and download media[/cyan]")
                    console.print(
                        "[dim]4.[/dim] [cyan]Export multiple chats[/cyan]")
                    console.print(
                        "[dim]5.[/dim] [cyan]Go back to chat selection[/cyan]")

                    action_choice = console.input(
                        "\n[bold]Enter your choice (1-5):[/bold] ")

                    if action_choice == '5':
                        # Go back to chat selection
                        continue

                    # Handle multiple chat export
                    if action_choice == '4':
                        console.print("\n[bold]Multiple Chat Export[/bold]")
                        console.print(
                            "Select multiple chats to export in batch.")

                        # Select multiple dialogs
                        multiple_dialogs = self.select_dialog(multiple=True)

                        if multiple_dialogs is None:
                            # User wants to quit
                            break
                        elif multiple_dialogs == 'refresh':
                            # User wants to refresh - update in place
                            if not await self.get_dialogs(is_refresh=True):
                                console.print(
                                    "\n[danger]Failed to refresh chats. Exiting...[/danger]")
                                break
                            continue

                        # Get export options
                        options = self.get_export_options()

                        # Create output directory
                        output_dir = os.path.join(os.getcwd(), 'exports')
                        os.makedirs(output_dir, exist_ok=True)

                        # Export multiple chats
                        await self.export_multiple_chats(
                            multiple_dialogs,
                            options['limit'],
                            output_dir,
                            options['start_date'],
                            options['end_date'],
                            options['include_photos'],
                            options['include_videos'],
                            options['include_documents'],
                            options['include_audio'],
                            options['include_stickers'],
                            options['include_voice'],
                            options['format_template'],
                            options['custom_name_info'] if options['use_custom_naming'] else None
                        )

                        continue

                    # Get export options if needed
                    options = None
                    if action_choice in ['1', '3']:
                        options = self.get_export_options()

                        # Handle custom file naming if enabled
                        output_file = options['output_file']
                        if options['use_custom_naming'] and options['file_pattern']:
                            # Replace {chat_name} with the actual chat name
                            chat_name = selected_dialog.name
                            # Sanitize chat name for file system
                            chat_name = ''.join(
                                c for c in chat_name if c.isalnum() or c in ' _-').strip()
                            # Replace spaces with underscores
                            chat_name = chat_name.replace(' ', '_')

                            # Apply the pattern
                            output_file = options['file_pattern'].replace(
                                "{chat_name}", chat_name)

                            # Replace date and time placeholders
                            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                            current_time = datetime.datetime.now().strftime("%H%M")
                            output_file = output_file.replace(
                                "{date}", current_date).replace("{time}", current_time)

                            # Add file extension
                            output_file += options['file_extension']

                            # Update the output file in options
                            options['output_file'] = output_file

                            # Show the final file name
                            console.print(
                                f"[dim]→ Final file name:[/dim] [cyan]{output_file}[/cyan]")

                    # Export messages if requested
                    if action_choice in ['1', '3']:
                        await self.export_chat(
                            selected_dialog,
                            options['limit'],
                            options['output_file'],
                            options['start_date'],
                            options['end_date'],
                            options['include_photos'],
                            options['include_videos'],
                            options['include_documents'],
                            options['include_audio'],
                            options['include_stickers'],
                            options['include_voice'],
                            options['format_template'],
                            options['custom_name_info'] if options['use_custom_naming'] else None
                        )

                    # Download media if requested
                    if action_choice in ['2', '3']:
                        # Ask for media download options
                        # Default to a 'media' subdirectory in the current directory
                        default_media_dir = os.path.join(os.getcwd(), 'media')
                        output_dir = console.input(
                            f"\n[bold]Enter output directory for media files:[/bold] (default: '{default_media_dir}'): ") or default_media_dir

                        # Create a subdirectory with the chat name for better organization
                        chat_name = selected_dialog.name
                        # Sanitize chat name for file system
                        chat_name = ''.join(
                            c for c in chat_name if c.isalnum() or c in ' _-').strip()
                        # Replace spaces with underscores
                        chat_name = chat_name.replace(' ', '_')

                        # Create a subdirectory for this specific chat
                        output_dir = os.path.join(output_dir, chat_name)
                        console.print(
                            f"[dim]→ Media will be saved to:[/dim] [cyan]{output_dir}[/cyan]")

                        # Ask for media type filtering
                        use_media_filter = console.input(
                            "\n[bold]Filter media types?[/bold] (y/n, default: n): ").lower() == 'y'

                        # Default to including all media types
                        include_photos = True
                        include_videos = True
                        include_documents = True
                        include_stickers = True

                        if use_media_filter:
                            # Create a panel for media options
                            media_panel = Panel(
                                "[bold]Media Type Filtering[/bold]\n\n"
                                "Select which media types to download.",
                                title="Media Options",
                                border_style="cyan",
                                box=ROUNDED
                            )
                            console.print(media_panel)

                            # Ask for each media type
                            include_photos = console.input(
                                "\n[bold]Include photos?[/bold] (y/n, default: y): ").lower() != 'n'
                            include_videos = console.input(
                                "[bold]Include videos?[/bold] (y/n, default: y): ").lower() != 'n'
                            include_documents = console.input(
                                "[bold]Include documents?[/bold] (y/n, default: y): ").lower() != 'n'
                            include_stickers = console.input(
                                "[bold]Include stickers?[/bold] (y/n, default: y): ").lower() != 'n'

                            # Show summary of selected options
                            console.print(
                                "\n[bold]Media types to include:[/bold]")
                            console.print(
                                f"[dim]→ Photos:[/dim] [cyan]{'Yes' if include_photos else 'No'}[/cyan]")
                            console.print(
                                f"[dim]→ Videos:[/dim] [cyan]{'Yes' if include_videos else 'No'}[/cyan]")
                            console.print(
                                f"[dim]→ Documents:[/dim] [cyan]{'Yes' if include_documents else 'No'}[/cyan]")
                            console.print(
                                f"[dim]→ Stickers:[/dim] [cyan]{'Yes' if include_stickers else 'No'}[/cyan]")

                        # Use the same date range as the export if available
                        start_date = options['start_date'] if options else None
                        end_date = options['end_date'] if options else None
                        limit = options['limit'] if options else DEFAULT_MESSAGE_LIMIT

                        await self.download_media(
                            selected_dialog,
                            limit,
                            output_dir,
                            start_date,
                            end_date,
                            include_photos,
                            include_videos,
                            include_documents,
                            include_stickers
                        )

                    # Ask if user wants to export another chat
                    another = console.input(
                        "\n[bold]Do you want to process another chat?[/bold] (y/n): ")
                    if another.lower() != 'y':
                        break
                    else:
                        # User wants to process another chat, refresh the dialog list
                        if not await self.get_dialogs(is_refresh=True):
                            console.print(
                                "\n[danger]Failed to refresh chats. Exiting...[/danger]")
                            break
                        # Display dialogs again
                        self.display_dialogs()

                except KeyboardInterrupt:
                    # Handle Ctrl+C gracefully
                    console.print(
                        "\n[warning]Operation cancelled by user.[/warning]")

                    # Ask if user wants to continue with the program
                    try:
                        continue_program = console.input(
                            "\n[bold]Do you want to continue using ChatShift?[/bold] (y/n): ")
                        if continue_program.lower() != 'y':
                            break
                        else:
                            # User wants to continue, refresh the dialog list
                            if not await self.get_dialogs(is_refresh=True):
                                console.print(
                                    "\n[danger]Failed to refresh chats. Exiting...[/danger]")
                                break
                            # Display dialogs again
                            self.display_dialogs()
                    except KeyboardInterrupt:
                        # If user presses Ctrl+C again, exit
                        console.print(
                            "\n[warning]Exiting ChatShift...[/warning]")
                        break

            # Disconnect from Telegram
            if self.client:
                async with status_context("[info]Disconnecting from Telegram...[/info]") as status:
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

        except KeyboardInterrupt:
            # Handle Ctrl+C at the top level
            console.print(
                "\n[warning]Operation cancelled by user. Exiting ChatShift...[/warning]")

            # Disconnect from Telegram if connected
            if self.client:
                try:
                    async with status_context("[info]Disconnecting from Telegram...[/info]") as status:
                        await self.client.disconnect()
                        status.update("[success]Disconnected![/success]")
                except Exception:
                    pass

        except Exception as e:
            # Handle any other exceptions
            console.print(f"\n[danger]An error occurred: {str(e)}[/danger]")

            # Disconnect from Telegram if connected
            if self.client:
                try:
                    async with status_context("[info]Disconnecting from Telegram...[/info]") as status:
                        await self.client.disconnect()
                        status.update("[success]Disconnected![/success]")
                except Exception:
                    pass

    async def export_multiple_chats(self, dialogs, limit, output_dir, start_date=None, end_date=None,
                                    include_photos=True, include_videos=True, include_documents=True,
                                    include_audio=True, include_stickers=True, include_voice=True,
                                    format_template=None, custom_name_info=None):
        """Export multiple chats to separate files"""
        # Create a directory for the exports if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Track successful and failed exports
        successful_exports = []
        failed_exports = []

        # Create an export panel with details
        export_details = [
            f"[bold]Exporting Multiple Chats:[/bold] [cyan]{len(dialogs)} chats[/cyan]",
            f"[bold]Output Directory:[/bold] [cyan]{output_dir}[/cyan]",
            f"[bold]Message Limit:[/bold] [cyan]{limit}[/cyan]",
        ]

        if start_date and end_date:
            export_details.append(
                f"[bold]Date Range:[/bold] [cyan]{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}[/cyan]")
        elif start_date:
            export_details.append(
                f"[bold]From Date:[/bold] [cyan]{start_date.strftime('%Y-%m-%d')}[/cyan]")
        elif end_date:
            export_details.append(
                f"[bold]To Date:[/bold] [cyan]{end_date.strftime('%Y-%m-%d')}[/cyan]")

        export_panel = Panel(
            "\n".join(export_details),
            title="Multiple Chat Export",
            border_style="cyan",
            box=ROUNDED
        )
        console.print(export_panel)

        # Process each dialog
        for i, dialog in enumerate(dialogs, 1):
            try:
                # Create a filename for this chat
                chat_name = dialog.name
                # Sanitize chat name for file system
                chat_name = ''.join(
                    c for c in chat_name if c.isalnum() or c in ' _-').strip()
                # Replace spaces with underscores
                chat_name = chat_name.replace(' ', '_')

                # Generate output file path
                if custom_name_info:
                    # Apply the pattern
                    file_name = custom_name_info['pattern'].replace(
                        "{chat_name}", chat_name)

                    # Replace date and time placeholders
                    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    current_time = datetime.datetime.now().strftime("%H%M")
                    file_name = file_name.replace(
                        "{date}", current_date).replace("{time}", current_time)

                    # Add file extension
                    file_name += custom_name_info['extension']
                else:
                    # Default filename
                    file_name = f"{chat_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt"

                output_file = os.path.join(output_dir, file_name)

                # Show progress
                console.print(
                    f"\n[bold][{i}/{len(dialogs)}] Exporting:[/bold] [cyan]{dialog.name}[/cyan]")

                # Export the chat
                await self.export_chat(
                    dialog,
                    limit,
                    output_file,
                    start_date,
                    end_date,
                    include_photos,
                    include_videos,
                    include_documents,
                    include_audio,
                    include_stickers,
                    include_voice,
                    format_template,
                    custom_name_info
                )

                successful_exports.append((dialog.name, output_file))

            except Exception as e:
                logger.error(f"Error exporting chat {dialog.name}: {str(e)}")
                failed_exports.append((dialog.name, str(e)))
                console.print(
                    f"[danger]Error exporting {dialog.name}: {str(e)}[/danger]")

        # Show summary
        console.print("\n[bold]Export Summary:[/bold]")
        console.print(
            f"[success]Successfully exported:[/success] [cyan]{len(successful_exports)}/{len(dialogs)}[/cyan]")

        if successful_exports:
            console.print("\n[bold]Successful exports:[/bold]")
            for name, path in successful_exports:
                console.print(
                    f"  [dim]•[/dim] [cyan]{name}[/cyan] → [dim]{path}[/dim]")

        if failed_exports:
            console.print("\n[bold]Failed exports:[/bold]")
            for name, error in failed_exports:
                console.print(
                    f"  [dim]•[/dim] [danger]{name}[/danger] → [dim]{error}[/dim]")

        return output_dir

    async def download_media(self, dialog, limit, output_dir, start_date=None, end_date=None,
                             include_photos=True, include_videos=True, include_documents=True,
                             include_stickers=True):
        """Download media files from a chat"""
        # Create an export panel with details
        export_details = [
            f"[bold]Downloading Media from:[/bold] [cyan]{dialog.name}[/cyan]",
            f"[bold]Message Limit:[/bold] [cyan]{limit}[/cyan]",
            f"[bold]Output Directory:[/bold] [cyan]{output_dir}[/cyan]"
        ]

        # Add date range information if provided
        if start_date:
            export_details.append(
                f"[bold]Start Date:[/bold] [cyan]{start_date.strftime('%Y-%m-%d')}[/cyan]")
        if end_date:
            export_details.append(
                f"[bold]End Date:[/bold] [cyan]{(end_date - datetime.timedelta(days=1)).strftime('%Y-%m-%d')}[/cyan]")

        # Add media type information
        media_types = []
        if not (include_photos and include_videos and include_documents and include_stickers):
            if include_photos:
                media_types.append("Photos")
            if include_videos:
                media_types.append("Videos")
            if include_documents:
                media_types.append("Documents")
            if include_stickers:
                media_types.append("Stickers")

            if media_types:
                export_details.append(
                    f"[bold]Media Types:[/bold] [cyan]{', '.join(media_types)}[/cyan]")
            else:
                export_details.append(
                    f"[bold]Media Types:[/bold] [warning]None (empty download)[/warning]")
        else:
            export_details.append(
                f"[bold]Media Types:[/bold] [cyan]All[/cyan]")

        export_panel = Panel(
            "\n".join(export_details),
            title="Media Download Details",
            border_style="cyan",
            box=ROUNDED
        )
        console.print(export_panel)

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Download media files
        async with status_context("[bold cyan]Downloading media files...[/bold cyan]") as status:
            # Get messages
            message_count = 0
            media_count = 0
            batch_size = 100  # Process messages in batches for better performance

            # Define filter function for better performance
            def media_filter(msg):
                # Apply date filter if provided
                if start_date and msg.date.replace(tzinfo=None) < start_date:
                    return False
                if end_date and msg.date.replace(tzinfo=None) >= end_date:
                    return False

                # Check if message has media
                if not msg.media:
                    return False

                # Skip media types that are not included
                if hasattr(msg.media, 'photo') and msg.media.photo and not include_photos:
                    return False

                if hasattr(msg.media, 'document') and msg.media.document:
                    # Check document type
                    if hasattr(msg.media.document, 'mime_type') and msg.media.document.mime_type:
                        mime_type = msg.media.document.mime_type

                        # Skip videos if not included
                        if mime_type.startswith('video/') and not include_videos:
                            return False

                        # Skip documents if not included
                        if not (mime_type.startswith('image/') or
                                mime_type.startswith('video/') or
                                mime_type.startswith('audio/')) and not include_documents:
                            return False

                    # Skip stickers if not included
                    if hasattr(msg, 'sticker') and msg.sticker and not include_stickers:
                        return False

                # Message passed all filters
                return True

            # Process messages in batches for better performance
            offset_id = 0
            while True:
                # Get a batch of messages
                batch = await self.client.get_messages(dialog.entity, limit=batch_size, offset_id=offset_id)
                if not batch:
                    break

                # Update offset for next batch
                offset_id = batch[-1].id

                # Filter messages with media
                media_messages = [msg for msg in batch if media_filter(msg)]

                # Download media files in parallel for better performance
                download_tasks = []
                for message in media_messages:
                    try:
                        filename = f"{message.id}"
                        if hasattr(message.media, 'document') and message.media.document and hasattr(message.media.document, 'attributes'):
                            for attr in message.media.document.attributes:
                                if hasattr(attr, 'file_name') and attr.file_name:
                                    filename = attr.file_name
                                    break

                        # Ensure filename is unique
                        file_path = os.path.join(output_dir, filename)
                        if os.path.exists(file_path):
                            base, ext = os.path.splitext(filename)
                            filename = f"{base}_{message.id}{ext}"
                            file_path = os.path.join(output_dir, filename)

                        # Add download task
                        download_tasks.append(
                            message.download_media(file=file_path))
                    except Exception as e:
                        console.print(
                            f"[bold red]Error preparing media download:[/bold red] {str(e)}")

                # Execute downloads in parallel
                if download_tasks:
                    try:
                        # Use asyncio.gather for parallel downloads
                        await asyncio.gather(*download_tasks)
                        media_count += len(download_tasks)
                        status.update(
                            f"[bold cyan]Downloaded {media_count} media files...[/bold cyan]")
                    except Exception as e:
                        console.print(
                            f"[bold red]Error downloading media:[/bold red] {str(e)}")

                # Update message count
                message_count += len(batch)
                status.update(
                    f"[bold cyan]Processed {message_count} messages, downloaded {media_count} media files...[/bold cyan]")

                # Check if we've reached the limit
                if limit > 0 and message_count >= limit:
                    break

            # Show completion message
            status.update(
                f"[bold green]Downloaded {media_count} media files from {message_count} messages![/bold green]")
            time.sleep(0.5)

        # Show success message with details
        success_details = [
            f"[bold green]✓ Media download completed successfully![/bold green]\n",
            f"[bold]Messages Processed:[/bold] [cyan]{message_count}[/cyan]",
            f"[bold]Media Files Downloaded:[/bold] [cyan]{media_count}[/cyan]",
            f"[bold]Output Directory:[/bold] [cyan]{output_dir}[/cyan]"
        ]

        # Add date range information if provided
        if start_date:
            success_details.append(
                f"[bold]Start Date:[/bold] [cyan]{start_date.strftime('%Y-%m-%d')}[/cyan]")
        if end_date:
            success_details.append(
                f"[bold]End Date:[/bold] [cyan]{(end_date - datetime.timedelta(days=1)).strftime('%Y-%m-%d')}[/cyan]")

        # Add media type information
        if media_types:
            success_details.append(
                f"[bold]Media Types:[/bold] [cyan]{', '.join(media_types)}[/cyan]")

        success_panel = Panel(
            "\n".join(success_details),
            title="Success",
            border_style="green",
            box=ROUNDED
        )
        console.print(success_panel)


async def main():
    """Main function"""
    cli = ChatShiftCLI()
    await cli.run()

if __name__ == "__main__":
    # Run the CLI
    asyncio.run(main())
