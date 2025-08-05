import os
import asyncio

from zona.plugins import PluginBase
from app.integrations.xero import XeroConnector


class Plugin(PluginBase):
    """Summarise invoice totals using the Xero connector."""

    def __init__(self) -> None:
        api_key = os.getenv("XERO_API_KEY", "")
        base_url = os.getenv("XERO_BASE_URL", "https://api.xero.com")
        self.connector = XeroConnector(api_key=api_key, base_url=base_url)

    def run(self, args: str, context: dict) -> dict:
        start_date = args.strip()
        if not start_date:
            return {"result": "Usage: !xero_summary <start_date>"}
        invoices = asyncio.run(self.connector.fetch_invoices(start_date))
        total = sum(inv.get("Total", 0) for inv in invoices)
        return {"result": f"Toplam fatura tutarı: ${total}"}

    def get_metadata(self) -> dict:
        return {
            "name": "xero_summary",
            "description": "Xero fatura özeti",
            "version": "1.0",
        }
