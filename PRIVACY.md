# Privacy Policy

## Data Collection
We collect the following types of user information when you interact with the application:

- Chat prompts and responses
- Session identifiers and timestamps
- Optional metadata you choose to provide

## Data Storage
Depending on your configuration, collected data may be stored in **Firestore** or in a **SQL database** such as SQLite or Postgres (`USE_FIRESTORE` / `DATABASE_URL`). In addition, all interactions are written to application logs, which may contain the same information.

## Data Retention
Stored session data and logs are kept for no longer than **30 days** by default. The retention period can be changed via the `MEMORY_RETENTION_SECONDS` environment variable. Expired data is automatically purged from the system.

## Data Deletion
You may request deletion of your data at any time. A running instance exposes `DELETE /memory/{session_id}` to remove a specific chat session immediately. For self-hosted deployments, you may also clear the database and logs directly. For hosted deployments, contact the maintainers to request removal of your data; we will respond within 30 days.

## GDPR Rights for EU Users
If you are located in the European Union, the General Data Protection Regulation (GDPR) provides the following rights:

- Right of access to your data
- Right to rectification of inaccurate data
- Right to erasure ("right to be forgotten")
- Right to restrict processing
- Right to data portability
- Right to object to processing

We process your data solely to provide and improve the service. To exercise your rights or ask questions about privacy, please contact the maintainers at the address provided in the project repository.
