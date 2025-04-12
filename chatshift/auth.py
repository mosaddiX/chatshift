"""
Authentication module for Telegram API
"""

import os
import logging
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt, Confirm

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Rich console
console = Console()

def load_env_vars():
    """Load environment variables from .env file"""
    load_dotenv()
    
    # Get credentials from environment variables
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE')
    username = os.getenv('TELEGRAM_USERNAME')
    
    # Check if credentials are available
    if not all([api_id, api_hash]):
        console.print("[bold red]Error:[/bold red] Telegram API credentials not found in .env file")
        api_id = Prompt.ask("[bold]Enter your Telegram API ID[/bold]")
        api_hash = Prompt.ask("[bold]Enter your Telegram API Hash[/bold]")
        phone = Prompt.ask("[bold]Enter your phone number (with country code)[/bold]")
        
        # Ask if user wants to save credentials
        if Confirm.ask("[bold]Save these credentials for future use?[/bold]"):
            with open('.env', 'w') as f:
                f.write(f"TELEGRAM_API_ID={api_id}\n")
                f.write(f"TELEGRAM_API_HASH={api_hash}\n")
                f.write(f"TELEGRAM_PHONE={phone}\n")
                if username:
                    f.write(f"TELEGRAM_USERNAME={username}\n")
                f.write(f"OUTPUT_FILE=telegram_chat_export.txt\n")
                f.write(f"MESSAGE_LIMIT=0\n")
    
    return api_id, api_hash, phone, username

async def authenticate():
    """Authenticate with Telegram API and return client"""
    api_id, api_hash, phone, username = load_env_vars()
    
    # Create the client and connect
    client = TelegramClient('chatshift_session', api_id, api_hash)
    await client.connect()
    
    console.print("[bold green]Connecting to Telegram...[/bold green]")
    
    # Check if already authorized
    if not await client.is_user_authorized():
        console.print("[bold yellow]Authentication required[/bold yellow]")
        
        # Send code request
        await client.send_code_request(phone)
        console.print(f"[bold]Verification code sent to {phone}[/bold]")
        
        # Get verification code from user
        code = Prompt.ask("[bold]Enter the verification code[/bold]")
        
        try:
            # Sign in with code
            await client.sign_in(phone, code)
        except SessionPasswordNeededError:
            # Two-step verification is enabled
            password = Prompt.ask("[bold]Enter your two-step verification password[/bold]", password=True)
            await client.sign_in(password=password)
    
    console.print("[bold green]Successfully authenticated with Telegram![/bold green]")
    return client
