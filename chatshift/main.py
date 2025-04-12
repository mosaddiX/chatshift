"""
Main entry point for ChatShift
"""

import asyncio
import os
import sys
import logging
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from chatshift import __version__
from chatshift.auth import authenticate
from chatshift.exporter import ChatExporter
from chatshift.search import MessageSearcher
from chatshift.formatter import WhatsAppFormatter

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Rich console
console = Console()

def display_welcome():
    """Display welcome message and version info"""
    welcome_text = f"""
[bold cyan]ChatShift v{__version__}[/bold cyan]
[italic]Telegram Chat Exporter[/italic]

Developed by [bold green]mosaddiX[/bold green]
    """
    console.print(
        Panel(welcome_text, title="Welcome to ChatShift", border_style="green"))

async def main():
    """Main entry point"""
    display_welcome()

    try:
        # Authenticate with Telegram
        client = await authenticate()

        # Create exporter and searcher
        exporter = ChatExporter(client)
        searcher = MessageSearcher(client)

        while True:
            # Display main menu
            console.print("\n[bold]Main Menu:[/bold]")
            console.print("1. Export chat")
            console.print("2. Search messages")
            console.print("3. Download media")
            console.print("4. Exit")
            
            choice = Prompt.ask("[bold]Select an option[/bold]", default="1")
            
            if choice == "1":
                # Export chat
                await export_chat(client, exporter)
            elif choice == "2":
                # Search messages
                await search_messages(client, exporter, searcher)
            elif choice == "3":
                # Download media
                await download_media(client, exporter)
            elif choice == "4":
                # Exit
                break
            else:
                console.print("[bold red]Invalid option. Please try again.[/bold red]")

        # Disconnect client
        await client.disconnect()
        console.print(
            "[bold green]Thank you for using ChatShift![/bold green]")

    except KeyboardInterrupt:
        console.print(
            "\n[bold yellow]Process interrupted by user.[/bold yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        logger.exception("An error occurred:")
        sys.exit(1)

async def export_chat(client, exporter):
    """Export a chat"""
    try:
        # Get and display dialogs
        dialogs = await exporter.get_dialogs()
        selected_dialog = await exporter.display_dialogs(dialogs)
        
        # Get export options
        options = await exporter.get_export_options()
        
        # Export selected chat
        output_file = await exporter.export_chat(selected_dialog, **options)
        
        return output_file
    except Exception as e:
        console.print(f"[bold red]Error exporting chat: {str(e)}[/bold red]")
        logger.exception("Error exporting chat:")
        return None

async def search_messages(client, exporter, searcher):
    """Search messages in a chat"""
    try:
        # Get and display dialogs
        dialogs = await exporter.get_dialogs()
        selected_dialog = await exporter.display_dialogs(dialogs)
        
        # Get search options
        search_options = await searcher.get_search_options()
        
        # Perform search
        messages = await searcher.search_messages(
            selected_dialog.entity,
            **search_options
        )
        
        # Display search results
        if await searcher.display_search_results():
            # Ask if user wants to export search results
            if Confirm.ask("[bold]Export search results to file?[/bold]", default=True):
                # Get output file
                output_file = Prompt.ask(
                    "[bold]Output file name[/bold]",
                    default="search_results.txt"
                )
                
                # Create formatter
                me = await client.get_me()
                formatter = WhatsAppFormatter(user_id=me.id)
                
                # Export search results
                await searcher.export_search_results(output_file, formatter)
        
        return True
    except Exception as e:
        console.print(f"[bold red]Error searching messages: {str(e)}[/bold red]")
        logger.exception("Error searching messages:")
        return False

async def download_media(client, exporter):
    """Download media from a chat"""
    try:
        # Get and display dialogs
        dialogs = await exporter.get_dialogs()
        selected_dialog = await exporter.display_dialogs(dialogs)
        
        # Get download options
        options = await exporter.get_download_options()
        
        # Download media
        output_dir = await exporter.download_media(selected_dialog, **options)
        
        return output_dir
    except Exception as e:
        console.print(f"[bold red]Error downloading media: {str(e)}[/bold red]")
        logger.exception("Error downloading media:")
        return None

def run():
    """Run the application"""
    asyncio.run(main())

if __name__ == "__main__":
    run()
