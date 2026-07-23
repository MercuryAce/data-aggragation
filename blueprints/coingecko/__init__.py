import time

import requests
from flask import (
    Blueprint,
    render_template,
    jsonify,
    request,
    session,
    abort,
    current_app
)
from flask_caching import Cache
from werkzeug.exceptions import HTTPException

from clients.cg_client import (
    get_market_data,
    get_coin_details,
    get_ohlc,
    get_global,
    get_trending,
    get_categories,
    get_search, get_exchanges, get_exchange_details,
)


def rate_limit(limiter, limit_str):
    """Helper decorator for conditional rate limiting"""

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
    """Abort if same key pressed too quickly."""
    if not allow_request(key, cooldown=cooldown):
        abort(429)


def guarded_render(template_name: str, fetch_context,):
    """
    Safely render a template that depends on an external API call.

    For page routes, failures are routed to global error pages.
    """
    try:
        context = fetch_context()

        if context is None:
            abort(404)

        return render_template(
            template_name,
            **context,
            error=None,
        )

    except HTTPException:
        raise

    except requests.exceptions.HTTPError as e:
        current_app.logger.exception(str(e))

        status_code = None
        if e.response is not None:
            status_code = e.response.status_code

        if status_code == 404:
            abort(404)

        if status_code == 429:
            abort(429)

        if status_code == 503:
            abort(503)

        if status_code == 504:
            abort(504)

        abort(502)

    except requests.exceptions.Timeout as e:
        current_app.logger.exception(str(e))
        abort(504)

    except requests.exceptions.ConnectionError as e:
        current_app.logger.exception(str(e))
        abort(503)

    except requests.exceptions.RequestException as e:
        current_app.logger.exception(str(e))
        abort(502)

    except Exception as e:
        current_app.logger.exception(str(e))
        abort(500)


def guarded_json(
        fetch_data,
        service_error_message="Unable to reach the service at the moment. Please try again.",
        generic_error_message="Something went wrong while processing your request.",
):
    """
    Safely return JSON from an external API-backed route.
    """
    try:
        data = fetch_data()
        return jsonify(data)

    except HTTPException:
        raise

    except requests.exceptions.HTTPError as e:
        current_app.logger.exception(str(e))

        status_code = None
        if e.response is not None:
            status_code = e.response.status_code

        if status_code == 404:
            return jsonify({"error": "Resource not found."}), 404

        if status_code == 429:
            return jsonify({"error": "Too many requests. Please try again shortly."}), 429

        if status_code == 503:
            return jsonify({"error": "Service temporarily unavailable."}), 503

        if status_code == 504:
            return jsonify({"error": "Request timed out."}), 504

        return jsonify({"error": service_error_message}), 502

    except requests.exceptions.Timeout as e:
        current_app.logger.exception(str(e))
        return jsonify({"error": "Request timed out."}), 504

    except requests.exceptions.ConnectionError as e:
        current_app.logger.exception(str(e))
        return jsonify({"error": "Service temporarily unavailable."}), 503

    except requests.exceptions.RequestException as e:
        current_app.logger.exception(str(e))
        return jsonify({"error": service_error_message}), 502

    except Exception as e:
        current_app.logger.exception(str(e))
        return jsonify({"error": generic_error_message}), 500

cg_bp = Blueprint('cg', __name__, url_prefix='')


def init_cg_blueprint(cache: Cache, limiter=None):
    @cg_bp.route('/')
    @cache.cached(timeout=300)
    @rate_limit(limiter, "5 per minute")
    def index():
        guard_request('index_last_hit', 5)

        return guarded_render(
            'index.html',
            fetch_context=lambda: {
                'coins': get_market_data(limit=250),
                'global_stats': get_global()["data"]
            },
        )

    @cg_bp.route('/coin/<coin_id>')
    @cache.cached(timeout=120)
    @rate_limit(limiter, "5 per minute")
    def coin(coin_id):
        guard_request(f'coin_last_hit_{coin_id}', cooldown=3)

        return guarded_render(
            'coin.html',
            fetch_context=lambda: {
                'coin': get_coin_details(coin_id),
            },
        )

    @cg_bp.route('/api/price-history/<coin_id>')
    @cache.cached(timeout=300, query_string=True)
    @rate_limit(limiter, "5 per minute")
    def price_history(coin_id):
        allowed_days = {7, 30, 90, 365}
        days = request.args.get('days', default=30, type=int)
        if days not in allowed_days:
            return jsonify({"error": "Invalid days parameter."}), 400

        return guarded_json(
            fetch_data=lambda: get_ohlc(coin_id, days=days),
            service_error_message="Unable to load price history at the moment. Please try again.",
        )

    @cg_bp.route('/trending')
    @cache.cached(timeout=120)
    @rate_limit(limiter, "5 per minute")
    def trending():
        guard_request('trending_last_hit', cooldown=5)

        return guarded_render(
            'trending.html',
            fetch_context=lambda: {
                'trending': get_trending(),
            },
        )

    @cg_bp.route('/categories')
    @cache.cached(timeout=120)
    @rate_limit(limiter, "5 per minute")
    def categories():
        guard_request('categories_last_hit', cooldown=5)

        return guarded_render(
            'categories.html',
            fetch_context=lambda: {
                'categories': get_categories(),
            },
        )

    @cg_bp.route('/search')
    @cache.cached(timeout=60, query_string=True)
    @rate_limit(limiter, "5 per minute")
    def search():
        query = request.args.get('q', '', type=str).strip()

        if not query:
            abort(400)

        guard_request(f'search_last_hit_{query.lower()}', cooldown=3)

        return guarded_render(
            'search.html',
            fetch_context=lambda: {
                'query': query,
                'results': get_search(query),
            },
        )

    @cg_bp.route('/exchanges')
    @cache.cached(timeout=120)
    @rate_limit(limiter, "5 per minute")
    def exchanges():
        guard_request('exchanges_last_hit', cooldown=5)

        return guarded_render(
            'exchanges.html',
            fetch_context=lambda: {
                'exchanges': get_exchanges(),
            },
        )

    @cg_bp.route('/exchange/<exchange_id>')
    @cache.cached(timeout=120)
    @rate_limit(limiter, "5 per minute")
    def exchange_detail(exchange_id):
        guard_request(f'exchange_last_hit_{exchange_id}', cooldown=3)

        def fetch_exchange_context():
            exchange = get_exchange_details(exchange_id)

            if not exchange:
                abort(404)

            return {
                'exchange': exchange,
            }

        return guarded_render(
            'exchange.html',
            fetch_context=fetch_exchange_context,
        )

    return cg_bp
