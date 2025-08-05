# Privacy Policy

## Data Collection
We collect the following types of user information when you interact with the application:

- Chat prompts and responses
- Session identifiers and timestamps
- Optional metadata you choose to provide

## Data Storage
Depending on your configuration, collected data may be stored in **Firestore** or in a **SQL database** such as SQLite or Postgres (`USE_FIRESTORE` / `DATABASE_URL`). In addition, all interactions are written to application logs, which may contain the same information.

## Data Retention
Stored data and logs are kept for no longer than **30 days** unless a longer period is required to comply with legal obligations. After this period the data is deleted or anonymized.

## Data Deletion
You may request deletion of your data at any time. For self-hosted deployments, remove the records from your database and purge any logs. For hosted deployments, contact the maintainers to request removal of your data; we will respond within 30 days.

## GDPR Rights for EU Users
If you are located in the European Union, the General Data Protection Regulation (GDPR) provides the following rights:

- Right of access to your data
- Right to rectification of inaccurate data
- Right to erasure ("right to be forgotten")
- Right to restrict processing
- Right to data portability
- Right to object to processing

We process your data solely to provide and improve the service. To exercise your rights or ask questions about privacy, please contact the maintainers at the address provided in the project repository.
