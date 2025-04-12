# ChatShift Testing Guide

This guide provides instructions for testing the key features of ChatShift v1.0.0.

## Prerequisites

Before testing, make sure you have:

1. Installed all dependencies: `pip install -r requirements.txt`
2. Set up your Telegram API credentials in a `.env` file
3. Authenticated with Telegram at least once

## Testing Multiple Chat Export

1. Run ChatShift: `python chatshift.py`
2. Select a chat from the list
3. When prompted for action, select option 4 "Export multiple chats"
4. Select multiple chats by entering their numbers one at a time
   - Notice how the prompt shows the count of selected chats (e.g., "Selected: 3 >")
   - Each time you select a chat, you'll see a confirmation message
   - The interface avoids duplicating the list after each selection
5. Enter 'v' to view all your selected chats in a table format
6. Enter 'd' when you're done selecting
7. Configure your export options (format, date range, etc.)
8. Verify that all selected chats are exported to the specified directory
9. Check that each chat has its own file with the correct naming convention

## Testing Export Statistics

1. Run ChatShift: `python chatshift.py`
2. Select a chat from the list
3. Choose option 1 "Export messages only"
4. Configure your export options
5. After the export completes, when prompted, choose 'y' to generate statistics
6. Verify that the statistics display shows:
   - Total message count
   - Message counts by type (text, media, service)
   - Media counts by type (photos, videos, documents, audio)
   - Top message senders
   - Date range and messages per day
7. Verify that a statistics file is created alongside the export file

## Testing Performance Optimizations

1. Run ChatShift: `python chatshift.py`
2. Select a chat with a large number of messages
3. Choose option 1 "Export messages only"
4. Set a high message limit (e.g., 1000+)
5. Note the time it takes to download and process the messages
6. Compare with previous versions if possible
7. Verify that batch processing is working by observing the progress updates

## Testing Media Downloads

1. Run ChatShift: `python chatshift.py`
2. Select a chat with various media types
3. Choose option 2 "Download media only"
4. Configure media filters (include/exclude photos, videos, documents, stickers)
5. Verify that only the selected media types are downloaded
6. Check that parallel downloads are working by observing multiple files being downloaded simultaneously

## Testing Format Options

1. Run ChatShift: `python chatshift.py`
2. Select a chat
3. Choose option 1 "Export messages only"
4. When prompted for format, try each of the available formats:
   - WhatsApp
   - Telegram
   - Discord
   - Simple
   - No Header
   - Custom
5. For custom format, test different date formats and message templates
6. Verify that each format produces the expected output
7. Check that the "No Header" option correctly omits the header

## Testing Exit and Goodbye Screens

1. **Normal Exit**:
   - Complete an export operation
   - When asked if you want to continue, select 'n'
   - Observe the elegant farewell screen with cyan styling and sparkle symbols

2. **Keyboard Interrupt**:
   - Start an export operation
   - Press Ctrl+C to interrupt it
   - Observe the yellow-styled interrupted screen
   - When asked if you want to continue, select 'n'
   - Observe the goodbye screen

3. **Multiple Interrupts**:
   - Start an export operation
   - Press Ctrl+C to interrupt it
   - When asked if you want to continue, press Ctrl+C again
   - Observe the elegant exit screen

4. **Error Handling**:
   - Try to cause an error (e.g., by entering invalid input)
   - Observe how errors are displayed in elegant red panels

## Reporting Issues

If you encounter any issues during testing, please report them on the GitHub repository with:

1. A description of the issue
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Any error messages or logs
