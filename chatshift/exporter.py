"""
Telegram chat exporter module
"""

import os
import logging
import datetime
from telethon.tl.types import User, Chat
from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.prompt import Prompt, Confirm
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

    async def get_export_options(self):
        """Get export options from user"""
        # Use message limit from instance or default
        limit = self.message_limit if hasattr(self, 'message_limit') else 5000

        # Use output file from instance or default
        output_file = self.output_file if hasattr(
            self, 'output_file') else 'telegram_chat_export.txt'

        # Ask for message limit if not set in .env
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

        # Ask for date range filtering
        use_date_filter = Confirm.ask(
            "[bold]Filter by date range?[/bold]", default=False)
        start_date = None
        end_date = None

        if use_date_filter:
            # Get start date
            start_date_str = Prompt.ask(
                "[bold]Start date (YYYY-MM-DD, leave empty for no start date)[/bold]",
                default=""
            )
            if start_date_str:
                try:
                    start_date = datetime.datetime.strptime(
                        start_date_str, "%Y-%m-%d")
                except ValueError:
                    console.print(
                        "[yellow]Invalid start date format. Using no start date.[/yellow]")

            # Get end date
            end_date_str = Prompt.ask(
                "[bold]End date (YYYY-MM-DD, leave empty for no end date)[/bold]",
                default=""
            )
            if end_date_str:
                try:
                    end_date = datetime.datetime.strptime(
                        end_date_str, "%Y-%m-%d")
                except ValueError:
                    console.print(
                        "[yellow]Invalid end date format. Using no end date.[/yellow]")

        return {
            "limit": limit,
            "output_file": output_file,
            "start_date": start_date,
            "end_date": end_date
        }

    async def get_download_options(self):
        """Get media download options from user"""
        # Ask for output directory
        output_dir = Prompt.ask(
            "[bold]Output directory for media files[/bold]",
            default="media"
        )

        # Ask for media types to download
        console.print("[bold]Select media types to download:[/bold]")
        include_photos = Confirm.ask("Include photos?", default=True)
        include_videos = Confirm.ask("Include videos?", default=True)
        include_documents = Confirm.ask("Include documents?", default=True)
        include_audio = Confirm.ask("Include audio?", default=True)
        include_stickers = Confirm.ask("Include stickers?", default=False)
        include_voice = Confirm.ask("Include voice messages?", default=False)

        # Ask for message limit
        limit_input = Prompt.ask(
            "[bold]How many messages to scan? (0 for all)[/bold]",
            default="100"
        )
        try:
            limit = int(limit_input)
        except ValueError:
            limit = 100
            console.print(
                "[yellow]Invalid limit. Using default (100).[/yellow]")

        return {
            "output_dir": output_dir,
            "include_photos": include_photos,
            "include_videos": include_videos,
            "include_documents": include_documents,
            "include_audio": include_audio,
            "include_stickers": include_stickers,
            "include_voice": include_voice,
            "limit": limit
        }

    async def export_chat(self, dialog, limit=5000, output_file='telegram_chat_export.txt',
                          start_date=None, end_date=None):
        """Export selected chat to WhatsApp format"""
        # Initialize formatter with user's ID
        me = await self.client.get_me()
        self.formatter = WhatsAppFormatter(user_id=me.id)

        # Get chat entity and title
        entity = dialog.entity
        chat_title = dialog.name

        # Store the progress callback for TUI integration
        self.progress_callback = None

        # Log export start
        logger.info(f"Exporting chat: {chat_title}")
        console.print(
            f"[bold green]Exporting chat: [/bold green][bold cyan]{chat_title}[/bold cyan]")

        # Fetch messages
        if not hasattr(self, 'using_tui') or not self.using_tui:
            # Use progress bar for CLI
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
                        # Include all non-empty messages
                        if message:
                            messages.append(message)
                        progress.update(task, advance=1, total=actual_limit)

                    # Store messages for later reference
                    self.messages = messages

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
                    raise
        else:
            # Use callback for TUI
            try:
                # Set a reasonable default if limit is 0
                actual_limit = 5000 if limit == 0 else limit

                # Get messages
                messages = []
                message_count = 0

                async for message in self.client.iter_messages(entity, limit=actual_limit):
                    # Include all non-empty messages
                    if message:
                        messages.append(message)

                    # Update progress
                    message_count += 1
                    if self.progress_callback:
                        await self.progress_callback(message_count, actual_limit)

                # Store messages for later reference
                self.messages = messages

                # If no messages were found, show a warning
                if not messages:
                    logger.warning("No messages found in this chat.")
            except Exception as e:
                logger.exception("Error retrieving messages:")
                raise

        # Format messages
        logger.info("Formatting messages...")
        console.print("[bold green]Formatting messages...[/bold green]")
        formatted_messages = await self.formatter.format_messages(messages, chat_title)

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(formatted_messages))

        logger.info(f"Export complete! Saved to {output_file}")
        logger.info(f"Total messages exported: {len(messages)}")
        console.print(
            f"[bold green]Export complete! [/bold green]Saved to [bold cyan]{output_file}[/bold cyan]")
        console.print(
            f"[bold]Total messages exported: [/bold][bold cyan]{len(messages)}[/bold cyan]")

        return output_file

    def set_progress_callback(self, callback):
        """Set a callback function for progress updates"""
        self.progress_callback = callback

    def set_using_tui(self, using_tui=True):
        """Set whether the exporter is being used with the TUI"""
        self.using_tui = using_tui

    async def download_media(self, dialog, output_dir='media', limit=100,
                             include_photos=True, include_videos=True, include_documents=True,
                             include_audio=True, include_stickers=False, include_voice=False):
        """Download media from a chat"""
        # Get chat entity and title
        entity = dialog.entity
        chat_title = dialog.name

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Log download start
        logger.info(f"Downloading media from: {chat_title}")
        console.print(
            f"[bold green]Downloading media from: [/bold green][bold cyan]{chat_title}[/bold cyan]")

        # Initialize counters
        downloaded = 0
        skipped = 0
        errors = 0

        # Create progress bar
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            # Create progress task
            task = progress.add_task(f"[cyan]Scanning messages...", total=None)

            # Get messages with media
            messages = []
            async for message in self.client.iter_messages(entity, limit=limit):
                if message and hasattr(message, 'media') and message.media:
                    messages.append(message)
                progress.update(task, advance=1, total=limit)

            # Update progress task for downloading
            progress.update(task, description="[cyan]Downloading media...", total=len(
                messages), completed=0)

            # Download media
            for message in messages:
                try:
                    # Check media type
                    if hasattr(message.media, 'photo') and message.media.photo and include_photos:
                        # Download photo
                        path = await self.client.download_media(message, file=output_dir)
                        if path:
                            downloaded += 1
                        else:
                            skipped += 1
                    elif hasattr(message.media, 'document') and message.media.document:
                        # Check document attributes
                        attributes = message.media.document.attributes
                        is_video = any(getattr(attr, 'round_message', False) or getattr(
                            attr, 'supports_streaming', False) for attr in attributes)
                        is_audio = any(getattr(attr, 'voice', False) or getattr(
                            attr, 'title', False) for attr in attributes)
                        is_sticker = any(getattr(attr, 'sticker', False)
                                         for attr in attributes)

                        # Download based on type and user preferences
                        if (is_video and include_videos) or \
                           (is_audio and include_audio) or \
                           (is_sticker and include_stickers) or \
                           (not any([is_video, is_audio, is_sticker]) and include_documents):
                            path = await self.client.download_media(message, file=output_dir)
                            if path:
                                downloaded += 1
                            else:
                                skipped += 1
                        else:
                            skipped += 1
                    else:
                        skipped += 1
                except Exception as e:
                    logger.exception(f"Error downloading media: {str(e)}")
                    errors += 1

                # Update progress
                progress.update(task, advance=1)

        # Log download results
        logger.info(
            f"Media download complete! Downloaded: {downloaded}, Skipped: {skipped}, Errors: {errors}")
        console.print(f"[bold green]Media download complete![/bold green]")
        console.print(
            f"[bold]Downloaded:[/bold] [cyan]{downloaded}[/cyan] files")
        console.print(
            f"[bold]Skipped:[/bold] [yellow]{skipped}[/yellow] files")
        if errors > 0:
            console.print(f"[bold]Errors:[/bold] [red]{errors}[/red] files")

        return output_dir
