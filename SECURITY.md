# Security Testing Guidelines

This project includes optional scripts and dependencies for security scanning.
Install the development dependencies and run the helper script to perform
basic static and dependency analysis.

```bash
pip install -r requirements-dev.txt
./scripts/security_checks.sh
```

## Tools Included

### Static Code Analysis
- **Bandit** – `bandit -r path/to/your/project`
- **flake8** with `flake8-bugbear` and `flake8-bandit`
- **pylint** (use `pylint-django` or other plugins as needed)

### Dependency Security Scanning
- **pip-audit** – checks installed packages for known vulnerabilities.
- **Safety** – scans `requirements.txt` against vulnerability databases.

### Dynamic and Fuzz Testing
The repository does not automate dynamic or fuzz testing, but recommended tools include:
- **OWASP ZAP**, **Nikto**, **Nmap** for dynamic application security tests.
- **Atheris** and **Hypothesis** for fuzz testing.

### Manual Controls and Best Practices
- Validate authentication and authorization flows.
- Store credentials securely (e.g., environment variables or secret managers).
- Disable debug modes in production and prefer HTTPS with appropriate headers.

These guidelines help keep the project secure and can be integrated into
CI/CD pipelines as needed.
