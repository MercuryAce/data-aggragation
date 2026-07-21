import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("CG_API_KEY")
BASE_URL = os.getenv("CG_BASE_URL", "https://api.coingecko.com/api/v3")

headers = {}
if API_KEY:
    headers["x-cg-demo-api-key"] = API_KEY


# ---------------------- Public API Functions ---------------------- #

def ping():
    return _call(f"{BASE_URL}/ping")


def get_coins_list(include_platform=False):
    params = {
        "include_platform": str(include_platform).lower(),
        "limit": 250,
        "sparkline": True,
        "price_change_percentage": "1h, 24h, 7d, 14d, 30d, 200d, 1y",
    }
    return _call(f"{BASE_URL}/coins/list", params)


def get_market_data(vs_currency="usd", limit=250, page=1, **params):
    query = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": limit,
        "page": page,
        "sparkline": True,
        "price_change_percentage": "24h",
        **params,
    }
    return _call(f"{BASE_URL}/coins/markets", query)


def get_coin_details(coin_id, vs_currency="usd", **params):
    query = {
        "localization": False,
        "tickers": False,
        "community_data": False,
        "developer_data": False,
        "sparkline": False,
        **params,
    }
    return _call(f"{BASE_URL}/coins/{coin_id}", query)


def get_coin_tickers(coin_id, **params):
    return _call(f"{BASE_URL}/coins/{coin_id}/tickers", params)


def get_coin_history(coin_id, date, localization=False):
    params = {"date": date, "localization": localization}
    return _call(f"{BASE_URL}/coins/{coin_id}/history", params)


def get_market_chart(coin_id, days=30, vs_currency="usd", **params):
    query = {"vs_currency": vs_currency, "days": days, **params}
    return _call(f"{BASE_URL}/coins/{coin_id}/market_chart", query)


def get_market_chart_range(coin_id, from_ts, to_ts, vs_currency="usd", **params):
    query = {"vs_currency": vs_currency, "from": from_ts, "to": to_ts, **params}
    return _call(f"{BASE_URL}/coins/{coin_id}/market_chart/range", query)


def get_ohlc(coin_id, days=30, vs_currency="usd", **params):
    query = {"vs_currency": vs_currency, "days": days, **params}
    return _call(f"{BASE_URL}/coins/{coin_id}/ohlc", query)


def get_ohlc_range(coin_id, from_ts, to_ts, vs_currency="usd", interval="daily"):
    params = {
        "vs_currency": vs_currency,
        "from": from_ts,
        "to": to_ts,
        "interval": interval,
    }
    return _call(f"{BASE_URL}/coins/{coin_id}/ohlc/range", params)


def get_categories(order="market_cap_desc"):
    return _call(f"{BASE_URL}/coins/categories", {"order": order})


def get_categories_list():
    return _call(f"{BASE_URL}/coins/categories/list")


def get_simple_price(ids, vs_currencies="usd", **params):
    query = {"ids": ids, "vs_currencies": vs_currencies, **params}
    return _call(f"{BASE_URL}/simple/price", query)


def get_supported_vs_currencies():
    return _call(f"{BASE_URL}/simple/supported_vs_currencies")


def get_exchanges(per_page=100, page=1, **params):
    query = {"per_page": per_page, "page": page, **params}
    return _call(f"{BASE_URL}/exchanges", query)


def get_exchanges_list():
    return _call(f"{BASE_URL}/exchanges/list")


def get_exchange_details(exchange_id, **params):
    return _call(f"{BASE_URL}/exchanges/{exchange_id}", params)


def get_search(query):
    return _call(f"{BASE_URL}/search", {"query": query})


def get_trending(**params):
    return _call(f"{BASE_URL}/search/trending", params)


def get_global():
    return _call(f"{BASE_URL}/global")


def get_global_market_cap_chart(days=30, vs_currency="usd"):
    params = {"days": days, "vs_currency": vs_currency}
    return _call(f"{BASE_URL}/global/market_cap_chart", params)


# ---------------------- Private Helper ---------------------- #

def _call(url: str, params: dict = None):
    response = requests.get(url, params=params or {}, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()