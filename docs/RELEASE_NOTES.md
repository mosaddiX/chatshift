# ChatShift 1.0.0 Release Notes

We're excited to announce the release of ChatShift 1.0.0! This marks the first stable release of ChatShift, a powerful tool for exporting Telegram chats to various text formats.

## What's New in 1.0.0

### Multiple Chat Export
- Export multiple chats in a single operation
- Streamlined selection interface that avoids duplicate output
- View all selected chats in a table format with the 'v' command
- Batch export to a dedicated exports directory

### Export Statistics and Summaries
- Generate detailed statistics about exported chats
- Message counts by type (text, media, service)
- Media counts by type (photos, videos, documents, audio)
- Top message senders with percentage breakdown
- Date range and messages per day analysis
- Export statistics to a separate file

### Performance Optimizations
- Batch processing for faster message retrieval
- Parallel media downloads for improved performance
- Optimized filtering for large chats
- Improved memory usage for large exports

### Multiple Export Formats
- WhatsApp format
- Telegram format
- Discord format
- Simple text format
- No Header format
- Custom format with full control over all aspects

### Media Handling
- Download media files with filtering options
- Include/exclude specific media types (photos, videos, documents, stickers, etc.)
- Option to export messages only, download media only, or both

### User Experience Improvements
- Elegant and minimal terminal interface
- Redesigned welcome screen with a more compact and modern appearance
- Real-time progress updates
- Improved error handling and recovery
- Session management and authentication improvements

## Breaking Changes
- Removed advanced search functionality to focus on core features
- Simplified the application structure to a single script for easier distribution

## Installation and Usage

### Installation
```bash
git clone https://github.com/mosaddiX/chatshift.git
cd chatshift
pip install -r requirements.txt
```

### Usage
```bash
python chatshift.py
```

Follow the interactive prompts to select and export your chats.

## Known Issues
- Very large chats (>10,000 messages) may experience slower performance
- Some media types may not download correctly if they require special handling

## Future Plans
- GUI interface option
- Export to additional formats (HTML, PDF)
- Enhanced chat visualization and statistics
- Integration with other messaging platforms
- Scheduled exports

## Feedback and Contributions
We welcome your feedback and contributions! Please report any issues or suggestions on our GitHub repository.

Thank you for using ChatShift!
