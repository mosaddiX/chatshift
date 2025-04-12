# ChatShift Development Roadmap

This document outlines the planned development path for ChatShift.

## Version 0.1 (Completed)
- ✅ Basic setup and authentication
- ✅ Simple command-line interface
- ✅ Telegram API integration
- ✅ Basic WhatsApp format export
- ✅ Single chat export functionality

## Version 0.2 (Completed)
- ✅ Improved WhatsApp format implementation
- ✅ Better handling of different message types
- ✅ Support for media messages
- ✅ Improved date formatting
- ✅ Basic error handling

## Version 0.3 (Completed)
- ✅ Enhanced interactive terminal interface
- ✅ Chat search functionality
- ✅ Progress indicators
- ✅ Color-coded messages
- ✅ User-friendly navigation

## Version 0.4 (Completed)
- ✅ Elegant, minimal CLI design
- ✅ Improved chat selection and display
- ✅ Real-time progress updates during message downloading
- ✅ Enhanced message formatting for all message types
- ✅ Better error handling and user feedback
- ✅ Support for service messages (group actions, etc.)
- ✅ In-place table refresh functionality
- ❌ Date range filtering (Implemented in v0.5)
- ❌ Format customization (Moved to v0.5)

## Version 0.5 (Completed)
- ✅ Date range filtering
- ✅ Include/exclude media options
- ✅ Output file naming options
- ✅ Custom file naming options with placeholders
- ✅ Dynamic file name generation based on chat name and date
- ✅ Format customization
- ✅ Multiple format templates (WhatsApp, Telegram, Discord, Simple, Custom)
- ✅ User-defined custom format with full control
- ❌ Message type filtering (removed due to implementation issues)
- ✅ Media download feature
- ✅ Improved error handling and recovery
- ✅ Option to choose between exporting messages, downloading media, or both

## Version 1.0 (Current)
- ✅ Multiple chat export functionality
- ✅ Improved multiple chat selection interface with streamlined view that avoids duplicate output
- ✅ Export statistics and summaries
- ✅ Performance optimizations with batch processing
- ✅ Parallel media downloads for faster processing
- ✅ Multiple export format options (WhatsApp, Telegram, Discord, Simple, Custom)
- ✅ Optional headers in exported files
- ✅ Improved error handling for network issues
- ✅ Session management and recovery
- ✅ Proper package structure with setup.py
- ✅ Comprehensive documentation
- ✅ Testing guide

- ❌ Preview functionality before export (postponed for future release)
- ❌ Caching for frequently accessed data (postponed for future release)
- ❌ Resume capability for interrupted exports (postponed for future release)
- ❌ First-run wizard (postponed for future release)
- ❌ Standalone executables (postponed for future release)
- ❌ Configuration wizard (postponed for future release)

- ~~TUI interface~~ (Removed: Simplified CLI approach proved more reliable and maintainable)

## Future Ideas [after v1 released]
- GUI interface option
- Export to different formats (HTML, PDF)
- Chat visualization and statistics
- Integration with other messaging platforms
- Scheduled exports
- Batch operations for multiple chats
- Configuration profiles for different export settings
- Backup and restore functionality
