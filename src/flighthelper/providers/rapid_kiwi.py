"""
Provider: Kiwi Cheap Flights (RapidAPI) — /round-trip endpoint
Returns: list[dict] → {"price": float, "deeplink": str}
"""
from typing import List, Dict
import os, requests

RAPID_KEY = os.environ["RAPID_KEY"]

HOST      = "kiwi-com-cheap-flights.p.rapidapi.com"
ENDPOINT  = f"https://{HOST}/round-trip"

HEADERS = {
    "X-RapidAPI-Key":  RAPID_KEY,
    "X-RapidAPI-Host": HOST,
}

def _extract(itinerary: Dict) -> Dict | None:
    """Pull price & deeplink from one itinerary blob."""
    try:
        edge  = itinerary["bookingOptions"]["edges"][0]["node"]
        price = float(edge["price"]["amount"])
        url   = "https://www.kiwi.com" + edge["bookingUrl"]
        return {"price": price, "deeplink": url}
    except (KeyError, IndexError, TypeError, ValueError):
        return None

def search(origin: str,
           dest: str,
           depart_after: str,
           arrive_before: str,
           limit: int = 12) -> List[Dict]:
    params = {
        "source":      f"IATA:{origin}",
        "destination": f"IATA:{dest}",
        "outboundDepartureDateFrom": depart_after,
        "outboundDepartureDateTo":   arrive_before,
        "adults": 1,
        "currency": "usd",
        "locale": "en",
        "limit": limit,
        "enableSelfTransfer":      "true",
        "allowOvernightStopover":  "true",
    }

    resp = requests.get(ENDPOINT, headers=HEADERS, params=params, timeout=20)
    resp.raise_for_status()
    rows = resp.json().get("itineraries", [])

    out: List[Dict] = []
    for itin in rows[:limit]:
        item = _extract(itin)
        if item:
            out.append(item)
    return out
