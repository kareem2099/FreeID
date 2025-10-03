# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-03

### Added
- Initial release of FreeID Telegram bot
- Fetch user information including ID, username, names, and permissions
- Multiple commands: /start, /myid, /username
- Environment variable support for bot token
- Comprehensive user data display
- MongoDB integration for user analytics
- Admin statistics command (/stats)
- Daily and weekly active user tracking
- Persistent data storage for user interactions

### Technical Details
- Built with Python and pyTelegramBotAPI
- Markdown formatted responses
- Error handling for missing data
- MongoDB for scalable data persistence
- Environment configuration with dotenv
- Real-time analytics calculations
