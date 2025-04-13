# ChatShift Usage Guide

This guide explains how to use ChatShift v1.0 to export your Telegram chats in various formats.

## Getting Started

### Prerequisites

Before using ChatShift, you need to:

1. Have Python 3.7 or higher installed
2. Obtain your Telegram API credentials from https://my.telegram.org/apps
3. Install ChatShift and its dependencies

### Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Telegram API credentials:
```
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=your_phone_number
OUTPUT_FILE=telegram_chat_export.txt
MESSAGE_LIMIT=0  # 0 for all messages
```

For detailed installation instructions, see [INSTALL.md](INSTALL.md).

## Basic Usage

Run the application:
```bash
python chatshift.py
```

The application will:
1. Connect to Telegram using your credentials
2. Display a list of your chats
3. Let you select a chat or multiple chats to export
4. Provide options for exporting messages, downloading media, or both
5. Allow you to customize the export format and options
6. Save the exported chat(s) to text file(s)

## Main Features

### Single Chat Export

1. Select a chat from the list
2. Choose one of the following options:
   - Export messages only
   - Download media only
   - Export messages and download media
3. Configure export options:
   - Format template (WhatsApp, Telegram, Discord, Simple, Custom)
   - Date range (optional)
   - Message limit
   - Include/exclude media types
   - File naming options

### Multiple Chat Export

1. Select option 4 "Export multiple chats" from the action menu
2. Select chats by entering their numbers
3. Use 'v' to view all selected chats
4. Enter 'd' when done selecting
5. Configure export options

### Media Downloads

When downloading media, you can filter by type:
- Photos
- Videos
- Documents
- Audio files
- Stickers
- Voice messages

### Export Statistics

After exporting, you can generate statistics about your chats:
- Message counts by type
- Media counts by type
- Top message senders
- Date range and messages per day

## Export Formats

ChatShift supports multiple export formats:

### WhatsApp Format
```
01/06/23, 21:10 - John Doe: Hello there!
01/06/23, 21:11 - Jane Smith: Hi John, how are you?
```

### Telegram Format
```
[01/06/2023 21:10:15] John Doe: Hello there!
[01/06/2023 21:11:30] Jane Smith: Hi John, how are you?
```

### Discord Format
```
John Doe | 01/06/2023 21:10
Hello there!

Jane Smith | 01/06/2023 21:11
Hi John, how are you?
```

### Simple Format
```
John Doe (01/06/23 21:10): Hello there!
Jane Smith (01/06/23 21:11): Hi John, how are you?
```

### Custom Format
You can define your own format with placeholders for date, time, sender, and message content.

## Keyboard Shortcuts

- 'q' - Quit the application
- 'r' - Refresh the chat list
- 'd' - Done selecting (in multiple chat mode)
- 'v' - View all selected chats (in multiple chat mode)

## Troubleshooting

If you encounter any issues:

1. Check your internet connection
2. Verify your Telegram API credentials
3. Make sure you have the required permissions to access the chats
4. Check the console for error messages
5. Try deleting the `.session` file and authenticating again

For more detailed troubleshooting, see [INSTALL.md](INSTALL.md).

## Future Features

Planned for future versions:
- GUI interface option
- Export to HTML and PDF formats
- Enhanced chat visualization and statistics
- Integration with other messaging platforms
- Scheduled exports

For a complete roadmap, see [ROADMAP.md](ROADMAP.md).
