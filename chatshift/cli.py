"""
Command-line interface for ChatShift
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
[italic]Telegram to WhatsApp Chat Exporter[/italic]

Developed by [bold green]mosaddiX[/bold green]
    """
    console.print(Panel(welcome_text, title="Welcome to ChatShift", border_style="green"))

async def main():
    """Main CLI entry point"""
    display_welcome()
    
    try:
        # Authenticate with Telegram
        client = await authenticate()
        
        # Create exporter
        exporter = ChatExporter(client)
        
        while True:
            # Get and display dialogs
            dialogs = await exporter.get_dialogs()
            selected_dialog = await exporter.display_dialogs(dialogs)
            
            # Export selected chat
            output_file = await exporter.export_chat(selected_dialog)
            
            # Ask if user wants to export another chat
            if not Confirm.ask("[bold]Do you want to export another chat?[/bold]"):
                break
        
        # Disconnect client
        await client.disconnect()
        console.print("[bold green]Thank you for using ChatShift![/bold green]")
    
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Process interrupted by user.[/bold yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        logger.exception("An error occurred:")
        sys.exit(1)

def run():
    """Run the CLI"""
    asyncio.run(main())
