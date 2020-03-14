"""SubscriptionTag Model"""
from .. import db


class SubscriptionTag(db.Model):
    """Relationship between Subscription and Tag"""
    __tablename__ = "subscription_tag"
    username = db.Column(db.String(32), primary_key=True)
    channel_id = db.Column(db.String(32), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"), primary_key=True)
    __table_args__ = (db.ForeignKeyConstraint(
        [username, channel_id],
        ["subscription.username", "subscription.channel_id"]), {})