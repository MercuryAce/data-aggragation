from flask import Flask
from flask_caching import Cache

from blueprints.coingecko import init_cg_blueprint

import markdown
# from models import db
app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 60})

# === Database Configuration ===
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crypto.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create db instance
# db.init_app(app)

cg_bp = init_cg_blueprint(cache)
app.register_blueprint(cg_bp)

# with app.app_context():
#     db.create_all()

def init_markdown(app):
    @app.template_filter('markdown')
    def markdownify(text):
        if not text:
            return ''
        return markdown.markdown(
            text,
            extensions=['tables', 'fenced_code', 'nl2br', 'codehilite'],
        )

init_markdown(app)

if __name__ == '__main__':
    app.run(debug=True)
