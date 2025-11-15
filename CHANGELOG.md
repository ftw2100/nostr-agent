# Changelog

## [Unreleased] - 2024

### Added

#### Security Features
- **Command Authentication**: Optional `AUTHORIZED_PUBKEYS` environment variable to restrict command access
  - If not set, all users can use commands (backward compatible, with warning)
  - Commands `!help` and `!status` are always allowed
- **Rate Limiting**: Per-user rate limiting for commands (10/hour) and guidance messages (5/hour)
  - Sliding window implementation with automatic cleanup
  - Prevents abuse and API cost overruns
- **Input Sanitization**: All user inputs sanitized to prevent injection attacks
  - Removes control characters
  - Enforces length limits (configurable per input type)
- **Content Deduplication**: Prevents posting duplicate or very similar content
  - SHA-256 hash-based exact matching
  - Normalizes content (lowercase, whitespace collapse) before comparison
  - Tracks last 100 posts
  - Note: Similarity threshold parameter exists but currently only exact matches are checked

#### Resilience Features
- **Circuit Breaker**: Protects LLM API calls from cascading failures
  - States: CLOSED → OPEN → HALF_OPEN
  - Configurable failure threshold (default: 5) and timeout (default: 60s)
  - Supports both sync and async operations
  - Automatically recovers when service is restored
- **Event Validation**: Validates Nostr events before publishing
  - Checks content existence, length (bytes), and event kind
  - Validates both before publishing and after receiving
  - Graceful error handling for edge cases

#### Configuration
- **Constants Module**: Centralized configuration constants (`src/constants.py`)
  - Nostr protocol limits (MAX_NOTE_LENGTH, MAX_NOTE_BYTES)
  - LLM configuration (MAX_LLM_TOKENS, LLM_TIMEOUT_SECONDS, LLM_TEMPERATURE)
  - Rate limiting configuration
  - Posting intervals and limits
  - All previously hardcoded values now configurable

#### Dependency Management
- **Pipenv Migration**: Migrated from venv to Pipenv
  - `Pipfile` with production and dev dependencies
  - Updated installation and startup scripts
  - Updated documentation

### Changed

#### Core Modules
- **`src/agent.py`**: Integrated rate limiting, content deduplication, and input sanitization
- **`src/command_handler.py`**: Added authorization checks and rate limiting
- **`src/config_manager.py`**: Added `get_authorized_users()` method
- **`src/llm_provider.py`**: Wrapped LLM calls with circuit breaker, uses constants
- **`src/nostr_client.py`**: Added event validation, uses constants for limits
- **`src/posting_loop.py`**: Enforced minimum posting interval (30 seconds)

#### Scripts
- **`scripts/install.sh`**: Migrated to Pipenv workflow
- **`scripts/start.sh`**: Uses Pipenv to run application
- **`scripts/test_connection.py`**: Redacted API key display for security

#### Documentation
- **`README.md`**: Updated with Pipenv instructions and security features
- **`.env.example`**: Added `AUTHORIZED_PUBKEYS` configuration option

### Fixed

#### Security
- API key exposure in test script output (now redacted)
- Missing command authentication (now optional but recommended)
- No rate limiting (now implemented)
- No input sanitization (now implemented)

#### Reliability
- Missing circuit breaker for LLM calls (now implemented)
- No event validation (now implemented)
- Magic numbers scattered throughout code (now centralized)

### Testing

- Updated all test fixtures to mock new components (RateLimiter, ContentDeduplicator)
- Added mocks for `get_authorized_users()` method
- All 58 tests passing

### Documentation

- Added comprehensive audit report
- Added implementation complete report
- Added migration summary
- Added test results and recommendations
- Added final status report

---

## Notes

### Content Deduplication Similarity
The `ContentDeduplicator` currently implements exact matching only. The `similarity_threshold` parameter exists for future enhancement but is not yet used. Future improvements could add:
- Levenshtein distance calculation
- Fuzzy matching algorithms
- Semantic similarity detection

### Backward Compatibility
All changes maintain backward compatibility:
- If `AUTHORIZED_PUBKEYS` is not set, all users can use commands (with warning)
- Default behavior unchanged if security features are not configured
- Existing configuration files continue to work

### Migration Notes
- Users should run `pipenv install --dev` after pulling changes
- Optional: Set `AUTHORIZED_PUBKEYS` in `.env` for production deployments
- No breaking changes to existing functionality
