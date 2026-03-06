# Security Policy

## Supported Versions

Security updates are applied to the latest `main` branch.

## Reporting a Vulnerability

Please do not open public issues for security vulnerabilities.

1. Create a private disclosure through repository security advisories.
2. Include reproduction steps, impact, and suggested mitigation.
3. Allow maintainers time to validate and patch before public disclosure.

## Secret Management

- Never commit `.env` files or API keys.
- Use managed secret stores in cloud environments.
- Rotate keys immediately if exposure is suspected.
