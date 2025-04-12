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

## Version 0.5 (Current)
- ✅ Date range filtering
- ✅ Include/exclude media options
- ✅ Output file naming options (Moved to v0.5)
- ✅ Custom file naming options with placeholders
- ✅ Dynamic file name generation based on chat name and date
- ❌ Format customization
- ❌ Message type filtering (removed due to implementation issues)
- ✅ Media download feature
- ✅ Improved error handling and recovery
- ✅ Option to choose between exporting messages, downloading media, or both
- ❌ Advanced search functionality
- ❌ Message content filtering
- ❌ Multiple chat export
- ❌ Export statistics and summaries
- ❌ Performance optimizations

## Version 1.0 (Planned)
### Error Handling and Stability
- Comprehensive error handling for network issues and API limits
- Session management and recovery
- Improved authentication error handling

### User Experience Enhancements
- Multiple export format options (WhatsApp, HTML, JSON, CSV)
- Preview functionality before export

### Performance Optimizations
- Batch processing for large chats
- Caching for frequently accessed data
- Optimize memory usage for large exports
- Resume capability for interrupted exports

### Documentation and Help
- Comprehensive in-app help
- User guides with screenshots
- Troubleshooting section
- First-run wizard

### Installation and Distribution
- Standalone executables for major platforms
- Proper PyPI packaging
- Configuration wizard
- Cross-platform compatibility testing

- ~~TUI interface~~ (Removed: Simplified CLI approach proved more reliable and maintainable)

## Future Ideas
- GUI interface option
- Export to different formats (HTML, PDF)
- Chat visualization and statistics
- Integration with other messaging platforms
- Backup and restore functionality
- Scheduled exports
- Batch operations for multiple chats
- Configuration profiles for different export settings
