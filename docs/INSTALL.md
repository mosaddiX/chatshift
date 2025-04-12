# ChatShift Installation Guide

This guide provides detailed instructions for installing and setting up ChatShift.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Telegram API credentials (API ID and API Hash)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/mosaddiX/chatshift.git
cd chatshift
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install directly using setup.py:

```bash
pip install .
```

### 3. Create a .env File

Create a file named `.env` in the root directory with the following content:

```
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=your_phone_number
OUTPUT_FILE=telegram_chat_export.txt
MESSAGE_LIMIT=0  # 0 for all messages
```

Replace the placeholders with your actual Telegram API credentials.

### 4. Obtaining Telegram API Credentials

1. Visit https://my.telegram.org/apps
2. Log in with your Telegram account
3. Create a new application if you don't have one
4. Copy the API ID and API Hash to your `.env` file

## Running ChatShift

After installation, you can run ChatShift using:

```bash
python chatshift.py
```

The first time you run ChatShift, you'll need to authenticate with Telegram. Follow the prompts to enter the verification code sent to your Telegram account.

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:
- Verify your API credentials in the `.env` file
- Make sure your phone number is in international format (e.g., +1234567890)
- Check your internet connection

### Dependency Issues

If you encounter issues with dependencies:
- Make sure you have Python 3.7 or higher installed
- Try updating pip: `pip install --upgrade pip`
- Install dependencies one by one to identify problematic packages

### Session Issues

If you encounter session-related issues:
- Delete the `.session` file in the root directory
- Restart the authentication process

## Additional Resources

- [Telegram API Documentation](https://core.telegram.org/api)
- [Python-Telegram Documentation](https://docs.telethon.dev/en/stable/)

For more help, please open an issue on the [GitHub repository](https://github.com/mosaddiX/chatshift).
