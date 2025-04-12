"""
Textual-based Terminal User Interface for ChatShift
"""

import asyncio
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Static, Input, Select, Label, DataTable, LoadingIndicator
from textual.reactive import reactive
from textual.binding import Binding
from textual.screen import Screen
from textual.message import Message

from telethon.tl.types import User, Chat, Channel, Dialog

from chatshift import __version__
from chatshift.auth import authenticate
from chatshift.exporter import ChatExporter

# Initialize Rich console
console = Console()


class WelcomeScreen(Screen):
    """Welcome screen with authentication"""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("enter", "authenticate", "Authenticate"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the welcome screen"""
        yield Header(show_clock=True)

        with Container(id="welcome-container"):
            yield Static(f"[bold cyan]ChatShift v{__version__}[/bold cyan]", id="title")
            yield Static("[italic]Telegram to WhatsApp Chat Exporter[/italic]", id="subtitle")
            yield Static(f"[bold green]Developed by mosaddiX[/bold green]", id="author")
            yield Static("", id="spacer")
            yield Static("Welcome to ChatShift! This tool helps you export your Telegram chats", id="welcome-text")
            yield Static("in WhatsApp format for easy sharing and backup.", id="welcome-text2")
            yield Static("", id="spacer2")
            yield Static("Press [bold]Enter[/bold] to authenticate with Telegram", id="instruction")
            yield Static("Press [bold]Q[/bold] to quit", id="quit-instruction")

        yield Footer()

    def action_authenticate(self) -> None:
        """Authenticate with Telegram"""
        self.app.push_screen("authenticating")


class AuthenticatingScreen(Screen):
    """Screen shown during authentication"""

    def compose(self) -> ComposeResult:
        """Compose the authenticating screen"""
        yield Header(show_clock=True)

        with Container(id="auth-container"):
            yield Static("[bold]Connecting to Telegram...[/bold]", id="auth-status")
            yield LoadingIndicator(id="auth-loader")

        yield Footer()

    async def on_mount(self) -> None:
        """Handle screen mount event"""
        # Start authentication in the background
        self.run_worker(self._authenticate())

    async def _authenticate(self) -> None:
        """Authenticate with Telegram"""
        try:
            # Authenticate with Telegram
            client = await authenticate()

            # Store client in app
            self.app.client = client

            # Create exporter
            self.app.exporter = ChatExporter(client)

            # Get dialogs
            self.app.dialogs = await self.app.exporter.get_dialogs()

            # Show main screen
            self.app.push_screen("main")
        except Exception as e:
            # Show error
            self.app.push_screen(
                ErrorScreen(f"Authentication failed: {str(e)}"),
                "error"
            )


class MainScreen(Screen):
    """Main screen with chat list and export options"""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("e", "export", "Export"),
        Binding("f", "filter", "Filter"),
    ]

    selected_dialog: reactive[Optional[Dialog]] = reactive(None)
    filter_text: reactive[str] = reactive("")

    def compose(self) -> ComposeResult:
        """Compose the main screen"""
        yield Header(show_clock=True)

        with Horizontal(id="main-container"):
            with Vertical(id="left-panel", classes="panel"):
                yield Static("[bold]Your Telegram Chats[/bold]", id="chats-title")
                yield Input(placeholder="🔍 Filter chats...", id="filter-input")
                yield DataTable(id="chats-table", zebra_stripes=True)

            with Vertical(id="right-panel", classes="panel"):
                yield Static("[bold]Export Options[/bold]", id="export-title")

                with Container(id="export-options"):
                    yield Static("Selected chat: [bold cyan]None[/bold cyan]", id="selected-chat")
                    yield Static("Message limit:", id="limit-label")
                    yield Input(value="5000", placeholder="0 for all messages", id="limit-input")
                    yield Static("Output file:", id="output-label")
                    yield Input(value="telegram_chat_export.txt", placeholder="Path to save exported chat", id="output-input")

                    with Horizontal(id="export-buttons"):
                        yield Button("📤 Export", id="export-button", variant="primary", disabled=True)
                        yield Button("🔄 Refresh", id="refresh-button")

        yield Footer()

    def on_mount(self) -> None:
        """Handle screen mount event"""
        # Populate the table
        self._populate_table()

    def _populate_table(self) -> None:
        """Populate the chats table with dialogs"""
        table = self.query_one("#chats-table", DataTable)
        table.clear()

        # Set up columns if not already done
        if not table.columns:
            table.add_columns(
                "ID",
                "Name",
                "Type",
                "Unread"
            )

        # Filter dialogs if needed
        filter_text = self.filter_text.lower()
        dialogs = [
            d for d in self.app.dialogs
            if not filter_text or filter_text in d.name.lower()
        ]

        # Add rows to the table
        for i, dialog in enumerate(dialogs, 1):
            entity = dialog.entity

            # Determine entity type and add appropriate icon
            if isinstance(entity, User):
                entity_type = "👤 User"
            elif isinstance(entity, Chat):
                entity_type = "👥 Group"
            else:
                entity_type = "📢 Channel"

            # Format unread count
            unread = f"[bold green]{dialog.unread_count}[/bold green]" if dialog.unread_count > 0 else "0"

            # Add row to table
            table.add_row(
                str(i),
                dialog.name,
                entity_type,
                unread
            )

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes"""
        if event.input.id == "filter-input":
            self.filter_text = event.value
            self._populate_table()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in the chats table"""
        try:
            # Get the selected row data
            table = self.query_one("#chats-table", DataTable)
            row_key = event.row_key
            row_data = table.get_row(row_key)

            # The first column contains the ID (1-based)
            row_id = int(row_data[0]) - 1

            # Get the dialog name from the table
            dialog_name = row_data[1]

            # Find the matching dialog in the app's dialog list
            for dialog in self.app.dialogs:
                if dialog.name == dialog_name:
                    self.selected_dialog = dialog

                    # Update the selected chat label
                    selected_chat = self.query_one("#selected-chat", Static)
                    selected_chat.update(
                        f"Selected chat: [bold cyan]{self.selected_dialog.name}[/bold cyan]")

                    # Enable the export button
                    export_button = self.query_one("#export-button", Button)
                    export_button.disabled = False
                    break
        except Exception as e:
            self.app.push_screen(
                ErrorScreen(f"Error selecting chat: {str(e)}"),
                "error"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "export-button":
            self.action_export()
        elif event.button.id == "refresh-button":
            self.action_refresh()

    def action_refresh(self) -> None:
        """Refresh the chat list"""
        self.app.push_screen("refreshing")

    def action_filter(self) -> None:
        """Focus the filter input"""
        self.query_one("#filter-input", Input).focus()

    def action_export(self) -> None:
        """Export the selected chat"""
        if self.selected_dialog is None:
            self.app.push_screen(
                ErrorScreen(
                    "No chat selected. Please select a chat to export."),
                "error"
            )
            return

        # Get export options
        limit_input = self.query_one("#limit-input", Input)
        output_input = self.query_one("#output-input", Input)

        try:
            limit = int(limit_input.value) if limit_input.value else 5000
        except ValueError:
            limit = 5000

        output_file = output_input.value or "telegram_chat_export.txt"

        # Store export options in app
        self.app.export_options = {
            "dialog": self.selected_dialog,
            "limit": limit,
            "output_file": output_file
        }

        # Show exporting screen
        self.app.push_screen("exporting")


class RefreshingScreen(Screen):
    """Screen shown while refreshing chats"""

    def compose(self) -> ComposeResult:
        """Compose the refreshing screen"""
        yield Header(show_clock=True)

        with Container(id="refreshing-container"):
            yield Static("[bold]Refreshing chats...[/bold]", id="refreshing-status")
            yield LoadingIndicator(id="refreshing-loader")

        yield Footer()

    async def on_mount(self) -> None:
        """Handle screen mount event"""
        # Start refreshing in the background
        self.run_worker(self._refresh())

    async def _refresh(self) -> None:
        """Refresh the chat list"""
        try:
            # Get dialogs
            self.app.dialogs = await self.app.exporter.get_dialogs()

            # Remove this screen and return to main
            if self.app.screen_stack and len(self.app.screen_stack) > 1:
                # If we're in the refresh screen, pop it to go back to main
                self.app.pop_screen()
            else:
                # If somehow we're not in the expected screen, explicitly push main
                self.app.push_screen("main")
        except Exception as e:
            # Show error
            self.app.push_screen(
                ErrorScreen(f"Refreshing failed: {str(e)}"),
                "error"
            )


class ExportingScreen(Screen):
    """Screen shown during export"""

    def compose(self) -> ComposeResult:
        """Compose the exporting screen"""
        yield Header(show_clock=True)

        with Container(id="exporting-container"):
            yield Static("[bold]Exporting chat...[/bold]", id="exporting-status")
            yield Static("", id="exporting-progress")
            yield LoadingIndicator(id="exporting-loader")

        yield Footer()

    async def on_mount(self) -> None:
        """Handle screen mount event"""
        # Start exporting in the background
        self.run_worker(self._export())

    async def _export(self) -> None:
        """Export the selected chat"""
        try:
            # Get export options
            dialog = self.app.export_options["dialog"]
            limit = self.app.export_options["limit"]
            output_file = self.app.export_options["output_file"]

            # Update status
            status = self.query_one("#exporting-status", Static)
            status.update(
                f"[bold]Exporting chat: [cyan]{dialog.name}[/cyan][/bold]")

            # Export chat
            self.app.exporter.message_limit = limit
            self.app.exporter.output_file = output_file
            output_file = await self.app.exporter.export_chat(dialog)

            # Store result
            self.app.export_result = {
                "dialog": dialog,
                "output_file": output_file,
                "message_count": len(self.app.exporter.messages)
            }

            # Show result screen
            self.app.push_screen("result")
        except Exception as e:
            # Show error
            self.app.push_screen(
                ErrorScreen(f"Export failed: {str(e)}"),
                "error"
            )


class ResultScreen(Screen):
    """Screen showing export result"""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("b", "back", "Back"),
        Binding("o", "open", "Open File"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the result screen"""
        yield Header(show_clock=True)

        with Container(id="result-container"):
            yield Static("[bold green]Export Complete![/bold green]", id="result-title")
            yield Static("", id="result-details")

            with Horizontal(id="result-buttons"):
                yield Button("Back", id="back-button")
                yield Button("Open File", id="open-button", variant="primary")

        yield Footer()

    def on_mount(self) -> None:
        """Handle screen mount event"""
        # Get export result
        dialog = self.app.export_result["dialog"]
        output_file = self.app.export_result["output_file"]
        message_count = self.app.export_result["message_count"]

        # Update details
        details = self.query_one("#result-details", Static)
        details.update(
            f"Chat: [bold cyan]{dialog.name}[/bold cyan]\n"
            f"Output file: [bold cyan]{output_file}[/bold cyan]\n"
            f"Messages exported: [bold cyan]{message_count}[/bold cyan]"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "back-button":
            self.action_back()
        elif event.button.id == "open-button":
            self.action_open()

    def action_back(self) -> None:
        """Go back to the main screen"""
        self.app.pop_screen()

    def action_open(self) -> None:
        """Open the exported file"""
        output_file = self.app.export_result["output_file"]

        try:
            # Open the file with the default application
            if os.name == 'nt':  # Windows
                os.startfile(output_file)
            else:  # macOS and Linux
                # Import subprocess here to avoid issues
                import subprocess
                try:
                    # Try the Linux command first
                    subprocess.run(['xdg-open', output_file], check=False)
                except FileNotFoundError:
                    try:
                        # Try the macOS command
                        subprocess.run(['open', output_file], check=False)
                    except FileNotFoundError:
                        # If all else fails, show an error
                        raise Exception(
                            "Could not find a program to open the file")
        except Exception as e:
            self.app.push_screen(
                ErrorScreen(f"Failed to open file: {str(e)}"),
                "error"
            )


class ErrorScreen(Screen):
    """Screen showing an error message"""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("b", "back", "Back"),
    ]

    def __init__(self, message: str) -> None:
        """Initialize with error message"""
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        """Compose the error screen"""
        yield Header(show_clock=True)

        with Container(id="error-container"):
            yield Static("[bold red]Error[/bold red]", id="error-title")
            yield Static(self.message, id="error-message")

            with Horizontal(id="error-buttons"):
                yield Button("Back", id="back-button", variant="primary")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "back-button":
            self.action_back()

    def action_back(self) -> None:
        """Go back to the previous screen"""
        self.app.pop_screen()


class ChatShiftApp(App):
    """Main ChatShift application"""

    TITLE = f"ChatShift v{__version__}"
    SUB_TITLE = "Telegram to WhatsApp Chat Exporter"

    CSS = """
    #welcome-container {
        width: 100%;
        height: 100%;
        align: center middle;
        background: $surface;
    }

    #welcome-container > Static {
        width: 100%;
        content-align: center middle;
        padding: 1;
    }

    #title {
        text-style: bold;
        color: $accent;
    }

    #subtitle {
        color: $text;
        text-style: italic;
    }

    #author {
        color: $success;
        margin-top: 1;
    }

    #spacer, #spacer2 {
        height: 1;
    }

    #welcome-text, #welcome-text2 {
        color: $text;
    }

    #instruction {
        margin-top: 1;
        color: $success;
    }

    #quit-instruction {
        color: $warning;
    }

    #auth-container, #refreshing-container, #exporting-container, #result-container, #error-container {
        width: 100%;
        height: 100%;
        align: center middle;
        background: $surface;
    }

    #auth-container > Static, #refreshing-container > Static, #exporting-container > Static {
        width: 100%;
        content-align: center middle;
        padding: 1;
    }

    #auth-loader, #refreshing-loader, #exporting-loader {
        width: 10;
        height: 1;
    }

    #main-container {
        width: 100%;
        height: 100%;
        background: $surface;
    }

    .panel {
        height: 100%;
        padding: 1;
        border: solid $primary;
    }

    #left-panel {
        width: 60%;
    }

    #right-panel {
        width: 40%;
    }

    #chats-title, #export-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #filter-input {
        margin-bottom: 1;
    }

    #chats-table {
        height: 1fr;
        border: solid $primary;
    }

    #export-options {
        margin-top: 2;
    }

    #export-options > Static {
        margin-bottom: 1;
    }

    #export-options > Input {
        margin-bottom: 1;
    }

    #export-buttons {
        margin-top: 2;
    }

    #export-buttons > Button {
        margin-right: 1;
    }

    #result-container > Static {
        width: 100%;
        content-align: center middle;
        padding: 1;
    }

    #result-title {
        color: $success;
        margin-bottom: 1;
    }

    #result-details {
        margin-bottom: 2;
    }

    #result-buttons {
        margin-top: 2;
    }

    #result-buttons > Button {
        margin-right: 1;
    }

    #error-container > Static {
        width: 100%;
        content-align: center middle;
        padding: 1;
    }

    #error-title {
        color: $error;
        margin-bottom: 1;
    }

    #error-message {
        margin-bottom: 2;
    }

    #error-buttons {
        margin-top: 2;
    }
    """

    SCREENS = {
        "welcome": WelcomeScreen(),
        "authenticating": AuthenticatingScreen(),
        "main": MainScreen(),
        "refreshing": RefreshingScreen(),
        "exporting": ExportingScreen(),
        "result": ResultScreen(),
    }

    def __init__(self) -> None:
        """Initialize the application"""
        super().__init__()
        self.client = None
        self.exporter = None
        self.dialogs = []
        self.export_options = {}
        self.export_result = {}

    def on_mount(self) -> None:
        """Handle application mount event"""
        # Show welcome screen
        self.push_screen("welcome")

    async def on_shutdown(self) -> None:
        """Handle application shutdown event"""
        # Disconnect Telegram client if connected
        if self.client and self.client.is_connected():
            await self.client.disconnect()


def run_app() -> None:
    """Run the ChatShift application"""
    app = ChatShiftApp()
    app.run()
