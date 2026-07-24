from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ApiCache(db.Model):
    __tablename__ = 'api_cache'

    key = db.Column(db.String(255), primary_key=True)
    payload = db.Column(db.JSON, nullable=False)
    fetched_at = db.Column(db.DateTime, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    source = db.Column(db.String(255), nullable=False, default='coingecko')

    def __repr__(self):
        return f'<ApiCache {self.key} @ {self.fetched_at}>'

# Association table (many-to-many)
creator_asset = db.Table(
    'creator_asset',
    db.Column('creator_id', db.Integer, db.ForeignKey('creators.id'), primary_key=True),
    db.Column('asset_id', db.Integer, db.ForeignKey('assets.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow),
)


class Creator(db.Model):
    __tablename__ = 'creators'

    id = db.Column(db.Integer, primary_key=True)
    handle = db.Column(db.String(100), unique=True, nullable=False)
    platform = db.Column(db.String(50))
    profile_url = db.Column(db.String(300), nullable=False)
    followers = db.Column(db.String(50))
    posts = db.Column(db.String(50))
    engagements = db.Column(db.String(50))
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assets = db.relationship('Asset', secondary=creator_asset, back_populates='creators')

    def __repr__(self):
        return f'<Creator {self.handle}>'


class Asset(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.String(200), unique=True, nullable=False)   # e.g. "bitcoin"
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    creators = db.relationship('Creator', secondary=creator_asset, back_populates='assets')

    def __repr__(self):
        return f'<Asset {self.coin_id}>'