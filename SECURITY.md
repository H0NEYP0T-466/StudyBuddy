# 🛡 Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them responsibly using one of the following methods:

### 1. GitHub Private Vulnerability Reporting

Use GitHub's private vulnerability reporting feature:
1. Go to the [Security tab](https://github.com/H0NEYP0T-466/StudyBuddy/security)
2. Click "Report a vulnerability"
3. Fill out the form with details

### 2. Email

Send details to: **security@studybuddy.example.com**

Please include:
- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### What to Expect

- **Initial Response**: We aim to acknowledge your report within **48 hours**
- **Progress Updates**: We'll keep you informed about our progress every 5-7 days
- **Fix Timeline**: We aim to release a fix within **30 days** for high-severity issues
- **Disclosure**: We'll coordinate with you on the disclosure timeline
- **Credit**: We'll acknowledge your contribution (unless you prefer to remain anonymous)

## Security Update Policy

### High Severity
- Immediate patch release
- Security advisory published
- Users notified via GitHub Security Advisories

### Medium Severity
- Patch included in next scheduled release
- Security advisory published
- Documented in release notes

### Low Severity
- Addressed in regular development cycle
- Documented in release notes

## Security Best Practices

When using StudyBuddy, please follow these security practices:

### API Keys and Secrets
- Never commit API keys to the repository
- Store sensitive data in `.env` files (never committed)
- Use environment variables for configuration
- Rotate API keys regularly

### MongoDB Security
- Use strong authentication credentials
- Enable MongoDB authentication
- Use TLS/SSL for connections
- Limit database user permissions

### File Uploads
- Only upload files from trusted sources
- Be cautious with files from unknown origins
- The application processes PDFs, DOCX, PPTX, and images

### Third-Party APIs
- Review API terms of service
- Understand data sharing implications
- Use the minimum required permissions
- Keep API client libraries updated

### Dependencies
- Regularly update dependencies
- Review dependency security advisories
- Use `npm audit` and `pip-audit` to check for vulnerabilities

## Known Security Considerations

### AI Model Integrations
- API keys are required for AI services (Gemini, LongCat, GitHub Models)
- Data sent to AI services is subject to their privacy policies
- Consider data sensitivity before using AI features

### Document Processing
- Uploaded documents are processed server-side
- Files are stored temporarily during processing
- RAG system stores processed text for search functionality

### Authentication
- Current version does not include user authentication
- Suitable for single-user/local deployments
- Multi-user deployments should add authentication

## Vulnerability Disclosure Policy

We follow responsible disclosure principles:

1. **Researcher Responsibilities**:
   - Allow reasonable time for fixes before public disclosure
   - Do not access or modify other users' data
   - Do not perform attacks that degrade service quality

2. **Our Commitments**:
   - Acknowledge reports promptly
   - Provide regular progress updates
   - Credit researchers appropriately
   - Not pursue legal action for good-faith research

## Security Hall of Fame

We appreciate security researchers who help keep StudyBuddy safe:

<!-- Contributors will be listed here -->
- No vulnerabilities reported yet

---

Thank you for helping keep StudyBuddy and our users safe! 🙏
