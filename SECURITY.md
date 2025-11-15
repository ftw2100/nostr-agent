# Security Policy

## Supported Versions

We actively support the latest version of the project. Security updates are provided for:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < Latest| :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please **do not** open a public issue. Instead, please report it privately:

1. **GitHub Security Advisory**: Use [GitHub's private vulnerability reporting](https://github.com/ftw2100/nostr-agent/security/advisories/new) (preferred)
2. **Email**: Contact the maintainer directly if GitHub advisory is not available

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Time

We aim to:
- Acknowledge receipt within 48 hours
- Provide an initial assessment within 7 days
- Keep you informed of progress

## Security Best Practices

### For Users

1. **Never commit secrets**: Always use `.env` files and ensure they're in `.gitignore`
2. **Use strong keys**: Generate secure Nostr private keys
3. **Restrict access**: Use `AUTHORIZED_PUBKEYS` to limit who can control your agent
4. **Keep updated**: Regularly update dependencies
5. **Review permissions**: Check file permissions on `.env` files (should be 600)

### For Developers

1. **Input validation**: Always validate and sanitize user inputs
2. **Secret management**: Never hardcode secrets or API keys
3. **Dependency updates**: Keep dependencies up to date
4. **Code review**: Review security-sensitive code carefully
5. **Testing**: Test security features thoroughly

## Known Security Considerations

- **Private Keys**: Nostr private keys are stored in environment variables. Ensure `.env` files are properly secured.
- **API Keys**: OpenRouter API keys should be kept secret and never committed.
- **Rate Limiting**: The agent includes rate limiting to prevent abuse, but users should configure `AUTHORIZED_PUBKEYS` for production use.
- **Input Sanitization**: All user inputs are sanitized, but users should be cautious when accepting guidance from untrusted sources.

## Security Features

- ✅ Environment variable-based secret management
- ✅ Input sanitization and validation
- ✅ Rate limiting for commands and guidance
- ✅ Content deduplication to prevent spam
- ✅ Optional command authentication via `AUTHORIZED_PUBKEYS`
- ✅ Circuit breaker for API calls
- ✅ Event validation before publishing

## Disclosure Policy

We follow responsible disclosure practices:
- Vulnerabilities will be fixed before public disclosure
- Credit will be given to reporters (unless they prefer anonymity)
- A security advisory will be published after the fix is available

Thank you for helping keep this project secure!
