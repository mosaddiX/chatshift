"""
Advanced search functionality for ChatShift
"""

import re
import logging
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Rich console
console = Console()

class MessageSearcher:
    """Search for messages in Telegram chats"""

    def __init__(self, client):
        """Initialize with Telegram client"""
        self.client = client
        self.search_results = []
        self.current_entity = None

    async def search_messages(self, entity, query, limit=100, offset_date=None, 
                             from_user=None, filter_type=None):
        """
        Search for messages in a chat
        
        Args:
            entity: The chat entity to search in
            query: The search query
            limit: Maximum number of messages to return
            offset_date: Only return messages before this date
            from_user: Only return messages from this user
            filter_type: Filter by message type (text, media, etc.)
            
        Returns:
            List of messages matching the search criteria
        """
        self.current_entity = entity
        
        try:
            # Log search start
            logger.info(f"Searching for '{query}' in {getattr(entity, 'title', getattr(entity, 'first_name', 'Unknown chat'))}")
            
            # Perform search
            messages = await self.client.get_messages(
                entity,
                search=query,
                limit=limit,
                offset_date=offset_date,
                from_user=from_user,
                filter=filter_type
            )
            
            # Store results
            self.search_results = messages
            
            return messages
        except Exception as e:
            logger.exception(f"Error searching messages: {str(e)}")
            console.print(f"[bold red]Error searching messages: {str(e)}[/bold red]")
            return []

    async def display_search_results(self, format_date=None):
        """
        Display search results in a table
        
        Args:
            format_date: Function to format dates (optional)
        """
        if not self.search_results:
            console.print("[yellow]No messages found matching your search criteria.[/yellow]")
            return
        
        # Create table
        table = Table(title=f"Search Results ({len(self.search_results)} messages)")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Date", style="green")
        table.add_column("From", style="blue")
        table.add_column("Message", style="white")
        
        # Add rows
        for i, message in enumerate(self.search_results, 1):
            # Format date
            if format_date:
                date_str = format_date(message.date)
            else:
                date_str = message.date.strftime("%Y-%m-%d %H:%M")
            
            # Get sender name
            if hasattr(message, 'sender') and message.sender:
                sender_name = getattr(message.sender, 'first_name', 'Unknown')
                if hasattr(message.sender, 'last_name') and message.sender.last_name:
                    sender_name += f" {message.sender.last_name}"
            else:
                sender_name = "Unknown"
            
            # Get message content (truncated)
            if hasattr(message, 'text') and message.text:
                content = message.text[:50] + ('...' if len(message.text) > 50 else '')
            elif hasattr(message, 'media') and message.media:
                content = "[Media message]"
            else:
                content = "[Service message]"
            
            table.add_row(str(i), date_str, sender_name, content)
        
        console.print(table)
        
        return True

    async def get_search_options(self):
        """
        Get search options from user
        
        Returns:
            Dictionary of search options
        """
        # Display search panel
        search_panel = Panel(
            "[bold]Advanced Search[/bold]\n\n"
            "Search for messages in the current chat.",
            title="Search Options",
            border_style="cyan"
        )
        console.print(search_panel)
        
        # Get search query
        query = Prompt.ask("[bold]Enter search query[/bold] (leave empty to search all messages)")
        
        # Get message limit
        limit_str = Prompt.ask("[bold]Maximum number of results[/bold]", default="100")
        try:
            limit = int(limit_str)
        except ValueError:
            limit = 100
            console.print("[yellow]Invalid limit. Using default (100).[/yellow]")
        
        # Get date filter
        use_date_filter = Confirm.ask("[bold]Filter by date?[/bold]", default=False)
        offset_date = None
        if use_date_filter:
            date_str = Prompt.ask(
                "[bold]Only show messages before date[/bold] (YYYY-MM-DD)",
                default=datetime.now().strftime("%Y-%m-%d")
            )
            try:
                offset_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                console.print("[yellow]Invalid date format. Date filter disabled.[/yellow]")
        
        # Get user filter
        use_user_filter = Confirm.ask("[bold]Filter by sender?[/bold]", default=False)
        from_user = None
        if use_user_filter:
            user_input = Prompt.ask("[bold]Enter username or user ID[/bold]")
            try:
                # Try to interpret as user ID
                if user_input.isdigit():
                    from_user = int(user_input)
                else:
                    # Try to resolve username
                    from_user = user_input
            except ValueError:
                console.print("[yellow]Invalid user ID. User filter disabled.[/yellow]")
        
        # Get message type filter
        use_type_filter = Confirm.ask("[bold]Filter by message type?[/bold]", default=False)
        filter_type = None
        if use_type_filter:
            filter_options = {
                "1": "Text messages",
                "2": "Photos",
                "3": "Videos",
                "4": "Documents",
                "5": "Audio",
                "6": "Links",
                "7": "Geo/Location",
                "8": "Contacts"
            }
            
            # Display filter options
            console.print("[bold]Message type options:[/bold]")
            for key, value in filter_options.items():
                console.print(f"  {key}. {value}")
            
            # Get user selection
            filter_choice = Prompt.ask("[bold]Select message type[/bold] (1-8)", default="1")
            
            # Map selection to filter type
            filter_map = {
                "1": "text",
                "2": "photo",
                "3": "video",
                "4": "document",
                "5": "audio",
                "6": "url",
                "7": "geo",
                "8": "contact"
            }
            
            filter_type = filter_map.get(filter_choice, None)
            if not filter_type:
                console.print("[yellow]Invalid filter type. Type filter disabled.[/yellow]")
        
        return {
            "query": query,
            "limit": limit,
            "offset_date": offset_date,
            "from_user": from_user,
            "filter_type": filter_type
        }

    async def export_search_results(self, output_file, formatter):
        """
        Export search results to a file
        
        Args:
            output_file: Path to output file
            formatter: Message formatter instance
            
        Returns:
            Path to output file
        """
        if not self.search_results:
            console.print("[yellow]No search results to export.[/yellow]")
            return None
        
        try:
            # Format messages
            chat_title = getattr(self.current_entity, 'title', 
                               getattr(self.current_entity, 'first_name', 'Search Results'))
            
            formatted_messages = await formatter.format_messages(self.search_results, chat_title)
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(formatted_messages))
            
            console.print(f"[bold green]Search results exported to:[/bold green] [cyan]{output_file}[/cyan]")
            return output_file
        
        except Exception as e:
            logger.exception(f"Error exporting search results: {str(e)}")
            console.print(f"[bold red]Error exporting search results: {str(e)}[/bold red]")
            return None
