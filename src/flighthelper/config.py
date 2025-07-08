"""
Centralised env/config loader.
"""
import os
from dotenv import load_dotenv
from importlib import import_module

# Load .env in local runs; production can inject real env directly
load_dotenv()

# -- keys ---------------------------------------------------------------
OPENAI_KEY  = os.environ["OPENAI_API_KEY"]
RAPID_KEY   = os.environ.get("RAPID_KEY")          # used by Rapid providers

# -- runtime knobs ------------------------------------------------------
GPT_MODEL   = os.getenv("GPT_MODEL", "gpt-4o-mini")  # swap to o3-deep-research later
PROVIDER_ID = os.getenv("FLIGHT_PROVIDER", "rapid_kiwi")

# Dynamically import the chosen provider module
try:
    provider_mod = import_module(f".providers.{PROVIDER_ID}", package=__package__)
except ModuleNotFoundError as e:
    raise RuntimeError(  # fail fast on bad env value
        f"✈️  Unknown FLIGHT_PROVIDER '{PROVIDER_ID}'. "
        f"Did you set it in .env?") from e

search_flights = provider_mod.search  # function pointer used by agent
