import os
from zona.plugins.base import PluginBase
from app.integrations.logo import LogoConnector


class Plugin(PluginBase):
    """Summarise invoice totals using the Logo connector."""

    def __init__(self) -> None:
        api_key = os.getenv("LOGO_API_KEY", "")
        base_url = os.getenv("LOGO_BASE_URL", "")
        self.connector = LogoConnector(api_key=api_key, base_url=base_url)

    def run(self, args: str, context: dict) -> dict:
        try:
            start_date, end_date = args.split()
        except ValueError:
            return {"result": "Usage: !invoice_summary <start> <end>"}
        invoices = self.connector.fetch_invoices(start_date, end_date)
        total = sum(inv.get("amount", 0) for inv in invoices)
        return {"result": f"Toplam fatura tutarı: {total} TL"}

    def get_metadata(self) -> dict:
        return {"name": "invoice_summary", "version": "0.1"}
