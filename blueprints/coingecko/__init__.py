import time

from flask import (
    Blueprint,
    render_template,
    jsonify,
    request,
    session,
    abort,
    current_app,
)
from flask_caching import Cache
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from services.coingecko_service import (
    CacheMissError,
    get_market_data,
    get_coin_details,
    get_ohlc,
    get_global,
    get_trending,
    get_categories,
    get_search,
    get_exchanges,
    get_exchange_details,
)


def rate_limit(limiter, limit_str):
    def decorator(f):
        if not limiter:
            return f
        return limiter.limit(limit_str)(f)

    return decorator


def allow_request(key, cooldown=5):
    now = time.time()
    last = session.get(key, 0)
    if now - last < cooldown:
        return False
    session[key] = now
    return True


def guard_request(key: str, cooldown: int):
    if not allow_request(key, cooldown=cooldown):
        abort(429)


def guarded_render(template_name: str, fetch_context):
    try:
        context = fetch_context()
        if context is None:
            abort(404)
        return render_template(template_name, **context, error=None)

    except HTTPException:
        raise

    except CacheMissError as e:
        current_app.logger.warning("Cache miss: %s", e)
        abort(503)

    except SQLAlchemyError:
        current_app.logger.exception("Cache database error")
        abort(503)

    except Exception:
        current_app.logger.exception("Unexpected error rendering %s", template_name)
        abort(500)


def guarded_json(fetch_data, *, not_found_message="Resource not found."):
    try:
        return jsonify(fetch_data())

    except HTTPException:
        raise

    except CacheMissError as e:
        current_app.logger.warning("Cache miss: %s", e)
        return jsonify({"error": "Data not available yet. Please try again shortly."}), 503

    except SQLAlchemyError:
        current_app.logger.exception("Cache database error")
        return jsonify({"error": "Data store temporarily unavailable."}), 503

    except Exception:
        current_app.logger.exception("Unexpected JSON route error")
        return jsonify({"error": "Something went wrong while processing your request."}), 500


cg_bp = Blueprint("cg", __name__, url_prefix="")


def init_cg_blueprint(cache: Cache, limiter=None):
    @cg_bp.route("/")
    @cache.cached(timeout=300)
    @rate_limit(limiter, "5 per minute")
    def index():
        guard_request("index_last_hit", cooldown=5)

        def fetch_context():
            coins, coins_at = get_market_data(limit=250)
            global_payload, global_at = get_global()
            return {
                "coins": coins,
                "global_stats": global_payload["data"],
                "last_updated": max(coins_at, global_at),
            }

        return guarded_render("index.html", fetch_context)

    @cg_bp.route("/coin/<coin_id>")
    @cache.cached(timeout=120)
    @rate_limit(limiter, "5 per minute")
    def coin(coin_id):
        guard_request(f"coin_last_hit_{coin_id}", cooldown=3)

        def fetch_context():
            coin_data, fetched_at = get_coin_details(coin_id)
            return {"coin": coin_data, "last_updated": fetched_at}

        return guarded_render("coin.html", fetch_context)

    @cg_bp.route("/api/price-history/<coin_id>")
    @cache.cached(timeout=300, query_string=True)
    @rate_limit(limiter, "5 per minute")
    def price_history(coin_id):
        allowed_days = {7, 30, 90, 365}
        days = request.args.get("days", default=30, type=int)
        if days not in allowed_days:
            return jsonify({"error": "Invalid days parameter."}), 400

        guard_request(f"price_history_last_hit_{coin_id}_{days}", cooldown=3)

        return guarded_json(lambda: get_ohlc(coin_id, days=days)[0])

    @cg_bp.route("/trending")
    @cache.cached(timeout=120)
    @rate_limit(limiter, "5 per minute")
    def trending():
        guard_request("trending_last_hit", cooldown=5)

        def fetch_context():
            trending_data, fetched_at = get_trending()
            return {"trending": trending_data, "last_updated": fetched_at}

        return guarded_render("trending.html", fetch_context)

    @cg_bp.route("/categories")
    @cache.cached(timeout=120)
    @rate_limit(limiter, "5 per minute")
    def categories():
        guard_request("categories_last_hit", cooldown=5)

        def fetch_context():
            categories_data, fetched_at = get_categories()
            return {"categories": categories_data, "last_updated": fetched_at}

        return guarded_render("categories.html", fetch_context)

    @cg_bp.route("/search")
    @cache.cached(timeout=60, query_string=True)
    @rate_limit(limiter, "5 per minute")
    def search():
        query = request.args.get("q", "", type=str).strip()
        if not query:
            abort(400)

        guard_request(f"search_last_hit_{query.lower()}", cooldown=3)

        def fetch_context():
            results, fetched_at = get_search(query)
            return {"query": query, "results": results, "last_updated": fetched_at}

        return guarded_render("search.html", fetch_context)

    @cg_bp.route("/exchanges")
    @cache.cached(timeout=120)
    @rate_limit(limiter, "5 per minute")
    def exchanges():
        guard_request("exchanges_last_hit", cooldown=5)

        def fetch_context():
            exchanges_data, fetched_at = get_exchanges()
            return {"exchanges": exchanges_data, "last_updated": fetched_at}

        return guarded_render("exchanges.html", fetch_context)

    @cg_bp.route("/exchange/<exchange_id>")
    @cache.cached(timeout=120)
    @rate_limit(limiter, "5 per minute")
    def exchange_detail(exchange_id):
        guard_request(f"exchange_last_hit_{exchange_id}", cooldown=3)

        def fetch_context():
            exchange, fetched_at = get_exchange_details(exchange_id)
            return {"exchange": exchange, "last_updated": fetched_at}

        return guarded_render("exchange.html", fetch_context)

    return cg_bp
