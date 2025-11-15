"""Application-wide constants."""

# Nostr Protocol Limits
MAX_NOTE_LENGTH = 2000  # Characters (well below Nostr's 32KB limit)
MAX_NOTE_BYTES = 32 * 1024  # Nostr protocol limit: 32KB

# LLM Configuration
MAX_LLM_TOKENS = 500  # Maximum tokens for LLM generation
LLM_TIMEOUT_SECONDS = 30.0  # LLM API timeout
LLM_TEMPERATURE = 0.9  # Creative temperature for shitposting

# Posting Configuration
MIN_POSTING_INTERVAL_SECONDS = 30  # Minimum interval to prevent spam
DEFAULT_POSTING_INTERVAL_MINUTES = 60
MAX_POSTING_INTERVAL_MINUTES = 1440  # 24 hours
MIN_POSTING_INTERVAL_MINUTES = 1

# Rate Limiting
DEFAULT_COMMAND_RATE_LIMIT = 10  # Commands per hour per user
DEFAULT_GUIDANCE_RATE_LIMIT = 5  # Guidance messages per hour per user
RATE_LIMIT_WINDOW_MINUTES = 60  # Rate limit window

# Content Deduplication
MAX_CONTENT_HISTORY = 100  # Number of posts to remember for deduplication
CONTENT_SIMILARITY_THRESHOLD = 0.9  # Similarity threshold (0.0-1.0)

# Input Sanitization
MAX_INPUT_LENGTH = 10000  # Maximum input length for general input
MAX_COMMAND_ARGS_LENGTH = 1000  # Maximum length for command arguments
MAX_GUIDANCE_LENGTH = 5000  # Maximum length for guidance messages

# Retry Configuration
DEFAULT_MAX_RETRIES = 3  # Default retry attempts
RETRY_BACKOFF_BASE = 2  # Exponential backoff base (2^attempt seconds)

# Circuit Breaker Configuration
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5  # Failures before opening circuit
CIRCUIT_BREAKER_TIMEOUT = 60  # Seconds before attempting half-open
CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS = 1  # Max calls in half-open state
