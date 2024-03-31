"""Functions to handle currency exchange."""

import json
import requests
import time
from django.conf import settings


class CurrencyRates:
    """Fetch current exchange rates for USD conversion."""

    CACHE = settings.CACHE['fx']
    ENDPOINT = "http://api.exchangeratesapi.io/v1/latest"

    def __init__(self):
        """Load rates from cache or fetch if expired."""
        self.rates = self._load_cache() or self._fetch_rates()

    def get_rate(self, currency):
        """Get conversion rate from USD to given currency."""
        usd = self.rates['USD']
        return self.rates[currency] / usd

    def _fetch_rates(self):
        """Create request and fetch."""
        url = (
            f"{self.ENDPOINT}?access_key={settings.EXCHANGERATESAPI_KEY}"
            "&symbols=USD,GBP,AUD"
            "&format=1"
        )
        print(f"Request URL: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(
                f"FX API request refused ({self.ENDPOINT})"
                f" (HTTP status {response.status_code})"
            )
        rates = response.json()['rates']
        self._cache(rates)
        return rates

    def _load_cache(self):
        """Read exchange rates from cache if not expired."""
        if (
            self.CACHE['path'].exists()
            and self.CACHE['path'].stat().st_mtime
            > time.time() - self.CACHE['expiry_seconds']
        ):
            with open(self.CACHE['path'], "r") as f:
                return json.load(f)

    def _cache(self, rates):
        """Write exchange rates to cache."""
        self.CACHE['path'].parent.mkdir(parents=True, exist_ok=True)
        with open(self.CACHE['path'], "w") as f:
            json.dump(rates, f)


def usd_to_usd(usd):
    """Blank function to return USD unaltered."""
    return round(usd, 2)


def gbx_to_usd(pence):
    """Convert GBP pence to USD."""
    return gbp_to_usd(pence / 100)


def gbp_to_usd(gbp):
    """Convert GBP to USD."""
    c = CurrencyRates()
    rate = c.get_rate('GBP')
    return round(gbp / rate, 2)


def aud_to_usd(aud):
    """Convert AUD to USD."""
    c = CurrencyRates()
    rate = c.get_rate('AUD')
    return round(aud / rate, 2)


exchange = {
    "USD": usd_to_usd,
    "GBX": gbx_to_usd,
    "GBP": gbp_to_usd,
    "AUD": aud_to_usd,
}
