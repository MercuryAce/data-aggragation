# CryptoDash

A server-rendered Flask cryptocurrency dashboard. All market data is fetched live from the
external CoinGecko API (`clients/cg_client.py`). There is no database, cache server, or message
broker to run — `flask-caching` and `flask-limiter` both use in-process memory. The SQLAlchemy
models in `models.py` are dormant (commented out in `app.py`). Error pages live in
`templates/errors/` and are registered via `handlers/errors.py`.

## Cursor Cloud specific instructions

### Environment
- Python 3.12. Dependencies are installed into a local virtualenv at `venv/` (gitignored). The
  update script recreates `venv/` and installs `requirements.txt`, so no manual install is
  normally needed. System package `python3.12-venv` is required to create the venv.
- Dependencies are declared in `requirements.txt`.

### Running the app (dev server)
- Run with the venv Python: `./venv/bin/python app.py` — serves on `http://127.0.0.1:5000`.
- Debug/auto-reload only turns on when `FLASK_DEBUG=true` (set in `.env`).
- The `.env` file is committed and holds the CoinGecko API key, `SECRET_KEY`/`DEV_SECRET_KEY`,
  and rate-limit / cache settings.

### Non-obvious gotchas
- Config is driven by `.env` (loaded via `load_dotenv()` in `clients/cg_client.py` at import
  time). The Flask reloader does NOT watch `.env`, so restart the server after editing it.
- `SECRET_KEY` is needed for sessions (every route writes to `session` via the anti–click-spam
  `allow_request` helper). `app.py` falls back to `DEV_SECRET_KEY` when `SECRET_KEY` is unset,
  and raises `RuntimeError` only when `FLASK_ENV=production` and no `SECRET_KEY` is set. Both keys
  are present in `.env`, so pages work out of the box in dev.
- Rate-limit env values must be full `flask-limiter` strings. `app.py` passes
  `RATELIMIT_DAILY` / `RATELIMIT_HOURLY` straight into `default_limits`, so a bare number like
  `334` raises `ValueError: couldn't parse rate limit string '334'` (500) on any route that has
  no explicit per-route limit (e.g. `/robots.txt`). Use the `"334 per day"` / `"52 per hour"`
  format. Blueprint routes set their own `5 per minute` limit and are unaffected.
- Outbound internet is required: all data comes from the CoinGecko API and the UI CSS/JS load
  from CDNs (jsdelivr, cloudflare).
- Per-route throttling: each page has a ~5s session cooldown plus a 5/minute limiter. Rapid
  repeated requests to the same route return HTTP 429 by design; space out requests when testing.
- The other API keys in `.env` (CoinMarketCap, LunarCrush, CryptoPanic, CryptoRank) are unused
  scaffolding for future features — only CoinGecko is wired up.

### Lint / test / build
- There is no test suite, linter config, or build step in this repo. "Build" = running the
  Flask dev server above.
