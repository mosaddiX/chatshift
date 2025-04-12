# Installing ChatShift

This guide provides step-by-step instructions for installing ChatShift on your system.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Telegram account
- Telegram API credentials (API ID and API Hash)

## Getting Telegram API Credentials

1. Visit https://my.telegram.org/auth and log in with your phone number
2. Go to "API development tools"
3. Create a new application (or use an existing one)
4. Note down your API ID and API Hash

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

### 3. Configure Environment Variables

Create a `.env` file in the project root directory with the following content:

```
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=your_phone_number
TELEGRAM_USERNAME=your_username
OUTPUT_FILE=telegram_chat_export.txt
MESSAGE_LIMIT=0
```

Replace the placeholders with your actual information:
- `your_api_id`: Your Telegram API ID (numeric)
- `your_api_hash`: Your Telegram API Hash (alphanumeric)
- `your_phone_number`: Your phone number in international format (e.g., +1234567890)
- `your_username`: Your Telegram username (optional)

### 4. Run ChatShift

```bash
python chatshift.py
```

On first run, you'll be asked to authenticate with Telegram. A verification code will be sent to your Telegram account, which you'll need to enter in the terminal.

## Installation as a Package (Optional)

If you want to install ChatShift as a Python package:

```bash
pip install -e .
```

This will install ChatShift in development mode, allowing you to run it from anywhere using:

```bash
chatshift
```

## Troubleshooting

### Authentication Issues

- Make sure your API ID and API Hash are correct
- Check that your phone number is in the correct format
- If you have two-factor authentication enabled, you'll need to enter your password

### Dependency Issues

If you encounter issues with dependencies, try:

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Permission Issues

If you get permission errors when running the script, try:

```bash
chmod +x chatshift.py
./chatshift.py
```

## Getting Help

If you encounter any issues not covered here, please:
1. Check the documentation in the `docs` directory
2. Open an issue on the GitHub repository
