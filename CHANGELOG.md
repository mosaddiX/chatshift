# Changelog

All notable changes to ChatShift will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-04-13

### Added
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
- Option to choose between exporting messages, downloading media, or both
- Graceful handling of keyboard interrupts (Ctrl+C)
- Improved error handling and recovery
- Format customization with multiple templates (WhatsApp, Telegram, Discord, Simple, No Header, Custom)
- Ability to customize date formats, message formats, and placeholders
- User-defined custom format with full control over all formatting aspects
- Option to include or exclude the header in exported chats
- Removed WhatsApp encryption message from default header
- Modular code structure for better maintainability
- Multiple chat export functionality
- Improved multiple chat selection interface with streamlined view that avoids duplicate output
- Export statistics and summaries
- Performance optimizations with batch processing and parallel downloads
- Redesigned welcome screen with a more compact and elegant appearance
- Removed TELEGRAM_USERNAME requirement for simpler setup
- Changed default message limit to 0 (all messages) for better user experience
- Improved exit handling with elegant panels instead of plain text messages
- Added graceful exit option after export/download completion
- Fixed duplicate chat list display when refreshing or selecting another chat
- Redesigned all exit/goodbye screens with stylish, colorful panels and Unicode symbols

### Fixed
- Fixed async context manager issue with status updates
- Improved error handling for async operations
- Fixed chat list refresh when selecting to process another chat
- Improved user experience when continuing after cancellation
- Improved media download organization with chat-specific subdirectories
- Added .gitignore rules to prevent media files from being tracked by Git

### Removed
- Message type filtering (text, media, service, forwarded, replies) due to implementation issues

## [0.4.0] - 2025-04-12

### Added
- Simplified and reliable command-line interface
- Improved chat selection and display
- Real-time progress updates during message downloading
- Enhanced message formatting for all message types
- Better error handling and user feedback
- Support for service messages (group actions, etc.)
- In-place table refresh functionality

### Changed
- Removed TUI approach in favor of a simpler, more reliable CLI
- Integrated all functionality into a single file for better maintainability
- Improved message retrieval to include all message types
- Enhanced file opening functionality across different operating systems

## [0.3.0] - 2023-06-30

### Added
- Enhanced interactive terminal interface using Textual
- Modern TUI with screens, widgets, and keyboard navigation
- Chat filtering functionality
- Progress indicators for message downloading
- Improved error handling and user feedback
- Command-line arguments for interface selection
- Fallback to CLI if TUI dependencies are not available

### Changed
- Restructured application to support both CLI and TUI
- Improved exporter to work with both interfaces
- Better progress reporting during export

## [0.2.0] - 2023-06-15

### Added
- Enhanced message type handling
- Improved WhatsApp format compatibility
- Support for various media types (photos, documents, links, locations, contacts, polls)
- File name detection for document attachments
- Default message limit increased to 5000
- Better error handling for message formatting

### Fixed
- Empty export issue
- Message retrieval improvements
- Format consistency with WhatsApp exports

## [0.1.0] - 2023-06-01

### Added
- Initial release
- Basic Telegram authentication
- Simple command-line interface
- WhatsApp-style message formatting
- Single chat export functionality
- Support for text messages
- Basic media message handling
- Deleted and edited message indicators
