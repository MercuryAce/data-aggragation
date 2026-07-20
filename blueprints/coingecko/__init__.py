from flask import Blueprint, render_template, jsonify, request
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

cg_bp = Blueprint('cg', __name__, url_prefix='')


def init_cg_blueprint(cache: Cache):

    @cg_bp.route('/')
    @cache.cached(timeout=300)
    def index():
        coins = get_market_data(limit=250)
        global_stats = get_global()["data"]

        return render_template(
            'index.html',
            coins=coins,
            global_stats=global_stats,
        )

    @cg_bp.route('/coin/<coin_id>')
    @cache.cached(timeout=120)
    def coin(coin_id):
        coin = get_coin_details(coin_id)

        return render_template(
            'coin.html',
            coin=coin,
        )

    @cg_bp.route('/api/price-history/<coin_id>')
    @cache.cached(timeout=300, query_string=True)
    def price_history(coin_id):
        days = request.args.get('days', default=30, type=int)
        data = get_ohlc(coin_id, days=days)
        return jsonify(data)

    @cg_bp.route('/trending')
    @cache.cached(timeout=120)
    def trending():
        trending_data = get_trending()
        return render_template('trending.html', trending=trending_data)

    @cg_bp.route('/categories')
    @cache.cached(timeout=120)
    def categories():
        categories_data = get_categories()
        return render_template('categories.html', categories=categories_data)

    @cg_bp.route('/search')
    @cache.cached(timeout=60)
    def search():
        # Get query parameter from URL (?q=...)
        query = request.args.get('q', '').strip()
        results = get_search(query) if query else None
        return render_template('search.html', query=query, results=results)

    @cg_bp.route('/exchanges')
    @cache.cached(timeout=120)
    def exchanges():
        exchanges = get_exchanges()
        return render_template('exchanges.html', exchanges=exchanges)

    @cg_bp.route('/exchange/<exchange_id>')
    @cache.cached(timeout=120)
    def exchange_detail(exchange_id):
        exchange = get_exchange_details(exchange_id)
        if not exchange:
            exchange = []
        return render_template('exchange.html', exchange=exchange)

    return cg_bp