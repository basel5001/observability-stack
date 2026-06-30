# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public issue.
2. Email security findings to: security@example.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will acknowledge receipt within 48 hours and provide a detailed response within 7 days.

## Security Measures

- All container images use official base images and are pinned to specific versions in production
- Non-root users in custom containers
- No secrets stored in configuration files; use environment variables or secret managers
- Network isolation via Docker bridge network
- Health checks on all services
- Alertmanager credentials stored externally
