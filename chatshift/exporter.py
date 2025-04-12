"""
Telegram chat exporter module
"""

import os
import logging
from telethon.tl.types import User, Chat
from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.prompt import Prompt
from rich.table import Table
from dotenv import load_dotenv

from chatshift.formatter import WhatsAppFormatter

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Rich console
console = Console()


class ChatExporter:
    """Export Telegram chats to WhatsApp format"""

    def __init__(self, client):
        """Initialize with Telegram client"""
        self.client = client
        self.formatter = None
        load_dotenv()
        self.output_file = os.getenv('OUTPUT_FILE', 'telegram_chat_export.txt')
        self.message_limit = int(os.getenv('MESSAGE_LIMIT', '0'))

    async def get_dialogs(self, limit=100):
        """Get user's dialogs (chats)"""
        console.print("[bold green]Loading your chats...[/bold green]")

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Fetching chats...", total=None)
            dialogs = await self.client.get_dialogs(limit=limit)
            progress.update(task, completed=100)

        return dialogs

    async def display_dialogs(self, dialogs):
        """Display dialogs in a table for selection"""
        table = Table(title="Your Chats")
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="magenta")
        table.add_column("Messages", justify="right")

        for i, dialog in enumerate(dialogs, 1):
            entity = dialog.entity
            entity_type = "User" if isinstance(
                entity, User) else "Group" if isinstance(entity, Chat) else "Channel"
            table.add_row(
                str(i),
                dialog.name,
                entity_type,
                str(dialog.unread_count)
            )

        console.print(table)

        # Get user selection
        selection = Prompt.ask(
            "[bold]Enter the ID of the chat you want to export[/bold]",
            default="1"
        )

        try:
            index = int(selection) - 1
            if 0 <= index < len(dialogs):
                return dialogs[index]
            else:
                console.print(
                    "[bold red]Invalid selection. Please try again.[/bold red]")
                return await self.display_dialogs(dialogs)
        except ValueError:
            console.print(
                "[bold red]Invalid input. Please enter a number.[/bold red]")
            return await self.display_dialogs(dialogs)

    async def export_chat(self, dialog):
        """Export selected chat to WhatsApp format"""
        # Initialize formatter with user's ID
        me = await self.client.get_me()
        self.formatter = WhatsAppFormatter(user_id=me.id)

        # Get chat entity and title
        entity = dialog.entity
        chat_title = dialog.name

        console.print(
            f"[bold green]Exporting chat: [/bold green][bold cyan]{chat_title}[/bold cyan]")

        # Ask for message limit if not set in .env
        limit = self.message_limit
        if limit == 0:
            limit_input = Prompt.ask(
                "[bold]How many messages to export? (0 for all)[/bold]",
                default="0"
            )
            try:
                limit = int(limit_input)
            except ValueError:
                limit = 0

        # Ask for output file
        output_file = Prompt.ask(
            "[bold]Output file name[/bold]",
            default=self.output_file
        )

        # Fetch messages with progress bar
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            # Create progress task
            task = progress.add_task(
                f"[cyan]Downloading messages...", total=None)

            # Get messages
            messages = []
            try:
                # Set a reasonable default if limit is 0
                actual_limit = 5000 if limit == 0 else limit

                # Get messages
                async for message in self.client.iter_messages(entity, limit=actual_limit):
                    # Skip system messages and empty messages
                    if message and (message.text or message.media):
                        messages.append(message)
                    progress.update(task, advance=1, total=actual_limit)

                # If no messages were found, show a warning
                if not messages:
                    console.print(
                        "[bold yellow]Warning: No messages found in this chat.[/bold yellow]")
                    console.print(
                        "[yellow]This could be due to privacy settings or the chat being empty.[/yellow]")
            except Exception as e:
                console.print(
                    f"[bold red]Error retrieving messages: {str(e)}[/bold red]")
                logger.exception("Error retrieving messages:")

        # Format messages
        console.print("[bold green]Formatting messages...[/bold green]")
        formatted_messages = await self.formatter.format_messages(messages, chat_title)

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(formatted_messages))

        console.print(
            f"[bold green]Export complete! [/bold green]Saved to [bold cyan]{output_file}[/bold cyan]")
        console.print(
            f"[bold]Total messages exported: [/bold][bold cyan]{len(messages)}[/bold cyan]")

        return output_file
