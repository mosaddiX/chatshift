# ChatShift Usage Guide

This guide explains how to use ChatShift to export your Telegram chats in WhatsApp format.

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
TELEGRAM_USERNAME=your_username
OUTPUT_FILE=telegram_chat_export.txt
MESSAGE_LIMIT=0  # 0 for all messages
```

## Basic Usage

Run the application:
```bash
python chatshift.py
```

The application will:
1. Connect to Telegram using your credentials
2. Display a list of your chats
3. Let you select a chat to export
4. Download and format the messages
5. Save the formatted chat to a text file

## Understanding the Output

The exported chat will be formatted like WhatsApp chats:
- Each message starts with a date and time stamp
- Followed by the sender's name
- Then the message content
- Media files are indicated with `<Media omitted>`
- Deleted messages show as `This message was deleted`
- Edited messages have a suffix `<This message was edited>`

Example:
```
01/06/23, 21:10 - Messages and calls are end-to-end encrypted. No one outside of this chat, not even WhatsApp, can read or listen to them. Tap to learn more.
02/06/23, 18:51 - John Doe: Hello there!
02/06/23, 18:52 - Jane Smith: Hi John, how are you?
02/06/23, 18:53 - John Doe: <Media omitted>
02/06/23, 18:54 - Jane Smith: This message was deleted
```

## Troubleshooting

If you encounter any issues:

1. Check your internet connection
2. Verify your Telegram API credentials
3. Make sure you have the required permissions to access the chats
4. Check the console for error messages

## Coming in Future Versions

- Customization options for the output format
- Filtering messages by date, type, or content
- Exporting multiple chats at once
- Advanced search functionality
