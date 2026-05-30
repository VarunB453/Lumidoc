# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.x.x  | ✅ Active support  |
| < 1.0   | ❌ No support     |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public GitHub issue
2. Email security concerns to: security@example.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 5 business days
- **Fix Timeline**: Based on severity
  - Critical: 24-48 hours
  - High: 1 week
  - Medium: 2 weeks
  - Low: Next release

## Security Practices

- All dependencies are regularly audited (Dependabot)
- CodeQL analysis runs on every PR
- Secrets are never committed to the repository
- JWT tokens have short expiration times
- All API endpoints require authentication (except public routes)
- Input validation on all user inputs
- SQL injection prevention via parameterized queries
- XSS prevention via Content Security Policy headers
- Rate limiting on authentication endpoints
