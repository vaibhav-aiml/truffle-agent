# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest  | ✅         |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. **Do not** open a public GitHub issue for security vulnerabilities.
2. Email your findings to the repository owner directly.
3. Include a description of the vulnerability, steps to reproduce, and potential impact.
4. You will receive an acknowledgment within 48 hours.

## Security Measures

This project implements the following security controls:

- **SQL Injection Prevention**: All database queries use parameterized statements with `?` placeholders.
- **Read-Only Query Enforcement**: A SQLite connection-level authorizer blocks all write/modify operations (INSERT, UPDATE, DELETE, DROP, ALTER, ATTACH, DETACH) for user-facing query execution paths.
- **Rate Limiting**: Per-session request throttling prevents abuse.
- **Input Validation**: Query length is capped to prevent prompt stuffing and cost inflation.
- **No Hardcoded Secrets**: All API keys and credentials are loaded from environment variables.
- **Dependency Pinning**: All direct dependencies are pinned to exact tested versions.

## Scope

This is a demonstration/portfolio project. It does not implement user authentication, role-based access control, or multi-tenant data isolation, as those are outside its intended scope.
