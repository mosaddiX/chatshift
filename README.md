# ChatShift

ChatShift is a Python-based tool to export Telegram chats into WhatsApp-like text format with an interactive terminal interface.

## Features

- Export Telegram chats to WhatsApp-like format
- Interactive and elegant terminal interface
- Customizable export options
- Filter messages by date, type, and content
- Support for various message types (text, media, links, etc.)

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
- **v0.2**: WhatsApp format implementation
- **v0.3**: Interactive terminal interface
- **v0.4**: Customization options
- **v0.5**: Advanced features
- **v1.0**: Final release

## Developer

Developed by mosaddiX

## License

MIT License
