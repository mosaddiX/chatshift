# Changelog

All notable changes to ChatShift will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-04-13

### Added
- Date range filtering for message exports
- Ability to filter messages by start and end dates
- Media type filtering (photos, videos, documents, audio, stickers, voice)
- Message type filtering (text, media, service, forwarded, replies)
- Selective media inclusion/exclusion options
- Custom file naming options with placeholders
- Dynamic file name generation based on chat name and date
- Enhanced export options interface
- Improved export details display
- Date validation with helpful error messages

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
