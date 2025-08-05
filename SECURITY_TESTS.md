# Security Testing

This project includes guidance for automated and manual security checks.

## 1. Static Code Analysis
Use static analysis tools to detect issues without executing code.

Install development tools:
```bash
pip install -r requirements.txt -r dev-requirements.txt
```

Run the analyzers:
```bash
bandit -r path/to/your/project
flake8 path/to/your/project
pylint path/to/your/project
```

## 2. Dependency Security Scanning
Ensure third‑party packages do not contain known vulnerabilities.

```bash
pip-audit
safety check -r requirements.txt
```

## 3. Dynamic Application Security Testing (DAST)
When the application is running, perform external scans such as:

- **OWASP ZAP** – automatic web vulnerability scanner.
- **Nikto** – web server configuration scanner.
- **Nmap** – network service and basic vulnerability scanner.

## 4. Fuzz Testing
Identify edge cases and input validation issues by generating randomized input.

- **Atheris** – Python fuzzing engine.
- **Hypothesis** – property‑based testing library.

## 5. Manual Controls and Best Practices
- Strong authentication and authorization (JWT, OAuth, RBAC/ABAC).
- Protect secrets with environment files or secret managers.
- Enable robust logging and monitoring (Sentry, ELK, Prometheus, etc.).
- Disable debug mode and enforce HTTPS, HSTS, CORS/CSRF/XSS protections.
