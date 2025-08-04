class BaseConnector:
    """Minimal interface for integration connectors."""

    def authenticate(self) -> str:
        """Return an access token or raise an error."""
        raise NotImplementedError
