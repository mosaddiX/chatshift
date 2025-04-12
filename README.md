# ChatShift

ChatShift is a Python-based tool to export Telegram chats into WhatsApp-like text format with an elegant and simple interactive terminal interface.

## Features

- Export Telegram chats to WhatsApp-like format
- Clean and intuitive command-line interface
- Customizable export options
- Support for various message types (text, media, links, etc.)
- Real-time progress updates during export

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

## Usage

Run the application:
```bash
python chatshift.py
```

Follow the interactive prompts to select and export your chats.

## Version History

- **v0.1**: Basic setup and authentication
- **v0.2**: Enhanced WhatsApp format implementation
- **v0.3**: Interactive terminal interface
- **v0.4**: Simplified CLI approach
- **v0.5**: Date range filtering (current)
- **v1.0**: Final release (planned)

## Features in v0.5 (Current)

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
- Option to download media after exporting chat

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

## Developer

Developed by mosaddiX

## License

MIT License
