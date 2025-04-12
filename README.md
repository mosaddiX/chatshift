# ChatShift

ChatShift is a Python-based tool to export Telegram chats into various text formats with an elegant and simple interactive terminal interface.

## Features

- Export Telegram chats to multiple formats (WhatsApp, Telegram, Discord, Simple, Custom)
- Multiple chat export in a single operation
- Export statistics and summaries
- Media downloading with filtering options
- Clean and intuitive command-line interface
- Customizable export options
- Support for various message types (text, media, links, etc.)
- Real-time progress updates during export
- Performance optimizations for faster processing

## Installation

1. Clone this repository:
```bash
git clone https://github.com/mosaddiX/chatshift.git
cd chatshift
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Telegram API credentials:
```
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=your_phone_number
TELEGRAM_USERNAME=your_username
OUTPUT_FILE=telegram_chat_export.txt
MESSAGE_LIMIT=0  # 0 for all messages
```

You can obtain your Telegram API credentials by creating an application at https://my.telegram.org/apps

For detailed installation instructions, see [INSTALL.md](docs/INSTALL.md).

## Usage

Run the application:
```bash
python chatshift.py
```

Follow the interactive prompts to select and export your chats.

For testing the application, see [TESTING.md](docs/TESTING.md).

### Multiple Chat Export

To export multiple chats at once:
1. Select option 4 "Export multiple chats" from the action menu
2. Select the chats you want to export by entering their numbers
3. Use 'v' to view all selected chats in a table format
4. Enter 'd' when you're done selecting
5. Configure your export options

The multiple chat selection interface now shows a clean, streamlined view that avoids duplicating the list of selected chats after each selection. Instead, it shows:
- A confirmation message when a chat is added
- The current count of selected chats in the prompt
- A reminder to use 'v' to view all selected chats periodically

### Export Statistics

After exporting a chat, you can generate statistics about the exported messages:
- Message counts by type (text, media, service)
- Media counts by type (photos, videos, documents, audio)
- Top message senders
- Date range and messages per day

## Version History

- **v0.1**: Basic setup and authentication
- **v0.2**: Enhanced WhatsApp format implementation
- **v0.3**: Interactive terminal interface
- **v0.4**: Simplified CLI approach
- **v0.5**: Date range filtering and media options
- **v1.0**: Multiple chat export, statistics, and performance optimizations (current)

ChatShift has now reached version 1.0, a stable release with all core features implemented. See [RELEASE_NOTES.md](docs/RELEASE_NOTES.md) for details about this release and [ROADMAP.md](docs/ROADMAP.md) for the development history and future plans.

## Features in v1.0 (Current)

- Multiple chat export in a single operation
- Export statistics and summaries
- Performance optimizations with batch processing
- Parallel media downloads for faster processing
- Multiple export formats (WhatsApp, Telegram, Discord, Simple, Custom)
- Optional headers in exported files
- Date range filtering for message exports
- Ability to filter messages by start and end dates
- Media type filtering (photos, videos, documents, audio, stickers, voice)
- Selective media inclusion/exclusion options
- Custom file naming options with placeholders
- Dynamic file name generation based on chat name and date
- Enhanced export options interface
- Improved export details display
- Date validation with helpful error messages
- Media download feature with filtering options (photos, videos, documents, stickers)
- Option to choose between exporting messages, downloading media, or both
- Graceful handling of keyboard interrupts (Ctrl+C)
- Improved error handling and recovery

## Features in v0.4

- Simplified and reliable command-line interface
- Improved chat selection and display
- Real-time progress updates during message downloading
- Enhanced message formatting for all message types
- Better error handling and user feedback
- Support for service messages (group actions, etc.)
- In-place table refresh functionality

## Features in v0.2

- Improved WhatsApp format compatibility
- Enhanced message type handling
- Support for various media types:
  - Photos and videos
  - Documents with file names
  - Links and web pages
  - Locations
  - Contacts
  - Polls
- Default message limit of 5000
- Better error handling

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## Developer

Developed by mosaddiX

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
