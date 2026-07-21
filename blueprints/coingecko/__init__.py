from flask import Blueprint, render_template, jsonify, request, session, abort
from flask_caching import Cache
from clients.cg_client import (
    get_market_data,
    get_coin_details,
    get_ohlc,
    get_global,
    get_trending,
    get_categories,
    get_search, get_exchanges, get_exchange_details,
)
import time

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


cg_bp = Blueprint('cg', __name__, url_prefix='')

def init_cg_blueprint(cache: Cache, limiter=None):

    @cg_bp.route('/')
    @cache.cached(timeout=300, query_string=True)
    @rate_limit(limiter, "5 per minute")
    def index():
        if not allow_request('index_last_hit', cooldown=5):
            abort(429)
        coins = get_market_data(limit=250)
        global_stats = get_global()["data"]

        return render_template(
            'index.html',
            coins=coins,
            global_stats=global_stats,
        )

    @cg_bp.route('/coin/<coin_id>')
    @cache.cached(timeout=120, query_string=True)
    @rate_limit(limiter, "5 per minute")
    def coin(coin_id):
        if not allow_request('coin_last_hit', cooldown=5):
            abort(429)
        coin = get_coin_details(coin_id)

        return render_template(
            'coin.html',
            coin=coin,
        )

    @cg_bp.route('/api/price-history/<coin_id>')
    @cache.cached(timeout=300, query_string=True)
    @rate_limit(limiter, "5 per minute")
    def price_history(coin_id):
        if not allow_request('price_last_hit', cooldown=5):
            abort(429)
        days = request.args.get('days', default=30, type=int)
        data = get_ohlc(coin_id, days=days)
        return jsonify(data)

    @cg_bp.route('/trending')
    @cache.cached(timeout=120, query_string=True)
    @rate_limit(limiter, "5 per minute")
    def trending():
        if not allow_request('trending_last_hit', cooldown=5):
            abort(429)
        trending_data = get_trending()
        return render_template('trending.html', trending=trending_data)

    @cg_bp.route('/categories')
    @cache.cached(timeout=120, query_string=True)
    @rate_limit(limiter, "5 per minute")
    def categories():
        if not allow_request('categories_last_hit', cooldown=5):
            abort(429)
        categories_data = get_categories()
        return render_template('categories.html', categories=categories_data)

    @cg_bp.route('/search')
    @cache.cached(timeout=60, query_string=True)
    @rate_limit(limiter, "5 per minute")
    def search():
        if not allow_request('search_last_hit', cooldown=5):
            abort(429)
        # Get query parameter from URL (?q=...)
        query = request.args.get('q', '').strip()
        results = get_search(query) if query else None
        return render_template('search.html', query=query, results=results)

    @cg_bp.route('/exchanges')
    @cache.cached(timeout=120, query_string=True)
    @rate_limit(limiter, "5 per minute")
    def exchanges():
        if not allow_request('exchanges_last_hit', cooldown=5):
            abort(429)
        exchanges = get_exchanges()
        return render_template('exchanges.html', exchanges=exchanges)

    @cg_bp.route('/exchange/<exchange_id>')
    @cache.cached(timeout=120, query_string=True)
    @rate_limit(limiter, "5 per minute")
    def exchange_detail(exchange_id):
        exchange = get_exchange_details(exchange_id)
        if not exchange:
            return render_template('exchange.html', exchange=None), 404
        return render_template('exchange.html', exchange=exchange)

    return cg_bp