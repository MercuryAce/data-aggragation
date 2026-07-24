"""Shared cache key builders — used by coingecko_service and sync_coingecko."""


def coin_list_key(include_platform=False) -> str:
    return f"coin_list_{include_platform}"


def markets_key(vs_currency="usd", limit=250, page=1) -> str:
    return f"markets_{vs_currency}_{limit}_{page}"


def coin_key(coin_id, vs_currency="usd") -> str:
    return f"coin_{coin_id}_{vs_currency}"


def coin_tickers_key(coin_id) -> str:
    return f"coin_tickers_{coin_id}"


def coin_history_key(coin_id, date, localization=False) -> str:
    return f"coin_history_{coin_id}_{date}_{localization}"


def market_chart_key(coin_id, days=30, vs_currency="usd") -> str:
    return f"market_chart_{coin_id}_{days}_{vs_currency}"


def market_chart_range_key(coin_id, from_ts, to_ts, vs_currency="usd") -> str:
    return f"market_chart_range_{coin_id}_{from_ts}_{to_ts}_{vs_currency}"


def ohlc_key(coin_id, days=30, vs_currency="usd") -> str:
    return f"ohlc_{coin_id}_{days}_{vs_currency}"


def ohlc_range_key(coin_id, from_ts, to_ts, vs_currency="usd", interval="daily") -> str:
    return f"ohlc_range_{coin_id}_{from_ts}_{to_ts}_{vs_currency}_{interval}"


def categories_key(order="market_cap_desc") -> str:
    return f"categories_{order}"


def categories_list_key() -> str:
    return "categories_list"


def simple_price_key(ids, vs_currencies="usd") -> str:
    return f"simple_price_{ids}_{vs_currencies}"


def supported_vs_currencies_key() -> str:
    return "supported_vs_currencies"


def exchanges_key(per_page=100, page=1) -> str:
    return f"exchanges_{per_page}_{page}"


def exchanges_list_key() -> str:
    return "exchanges_list"


def exchange_details_key(exchange_id) -> str:
    return f"exchange_details_{exchange_id}"


def search_key(query: str) -> str:
    return f"search_{query.strip().lower()[:55]}"


def trending_key() -> str:
    return "trending"


def global_key() -> str:
    return "global"


def global_market_cap_chart_key(days=30, vs_currency="usd") -> str:
    return f"global_market_cap_chart_{days}_{vs_currency}"
