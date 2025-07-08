"""
Smoke-test Kiwi /round-trip (RapidAPI host).

Run:  pytest -q tests/test_kiwi_roundtrip.py
"""
import os, requests, pytest
from dotenv import load_dotenv

load_dotenv()
HOST     = "kiwi-com-cheap-flights.p.rapidapi.com"
ENDPOINT = f"https://{HOST}/round-trip"

@pytest.mark.skipif("RAPID_KEY" not in os.environ, reason="RAPID_KEY not set")
def test_kiwi_roundtrip_smoke():
    params = {
        "source": "IATA:LIM",
        "destination": "IATA:CUR",
        "outboundDepartureDateFrom": "2025-09-10",
        "outboundDepartureDateTo":   "2025-09-13",
        "adults": 1,
        "currency": "usd",
        "limit": 3,
    }

    r = requests.get(
        ENDPOINT,
        headers={
            "X-RapidAPI-Key":  os.environ["RAPID_KEY"],
            "X-RapidAPI-Host": HOST,
        },
        params=params,
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()
    rows = data.get("itineraries", [])
    assert rows, "No itineraries returned"

    edge  = rows[0]["bookingOptions"]["edges"][0]["node"]
    price = edge["price"]["amount"]
    url   = "https://www.kiwi.com" + edge["bookingUrl"]
    print(f"✓  {price} USD — {url}")
