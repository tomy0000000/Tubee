"""Database for SQLAlchemy"""
from datetime import datetime
import enum
import urllib
import flask_login
from flask import url_for, current_app
from Tubee import db, bcrypt, YouTube_Service_Public
from . import helper
from .helper import hub

class UserSubscription(db.Model):
    __tablename__ = "user-subscription"
    subscriber_username = db.Column(db.String(30), db.ForeignKey("user.username"), primary_key=True)
    subscribing_channel_id = db.Column(db.String(30), db.ForeignKey("subscription.channel_id"), primary_key=True)
    tags = db.Column(db.PickleType, nullable=True)

class User(flask_login.UserMixin, db.Model):
    """
    username                username for identification (Max:30)
    password                user's login password
    master                  user is Tubee Master
    pushover_key            access key to Pushover Service
    youtube_credentials     access credentials to YouTube Service
    subscriptions           User's Subscription to YouTube Channels
    """
    __tablename__ = "user"
    username = db.Column(db.String(30), nullable=False, primary_key=True)
    password = db.Column(db.String(70), nullable=False, server_default=None, unique=False)
    master = db.Column(db.Boolean, nullable=True, server_default="0", unique=False)
    pushover_key = db.Column(db.String(40), nullable=True, server_default="", unique=False)
    youtube_credentials = db.Column(db.JSON, nullable=True, server_default="{}", unique=False)
    subscriptions = db.relationship("UserSubscription",
                                    foreign_keys=[UserSubscription.subscriber_username],
                                    backref=db.backref("subscribers", lazy="joined"),
                                    lazy="dynamic",
                                    cascade="all, delete-orphan")
    def __init__(self, username, password):
        self.username = username
        if len(password) < 6:
            raise ValueError("Password must be longer than 6 characters")
        elif len(password) > 30:
            raise ValueError("Password must be shorter than 30 characters")
        self.password = password
    def __repr__(self):
        return "<users %r>" %self.username
    def promote_to_master(self):
        self.master = True
    def setting_pushover_key(self, key):
        pass

    """UserMixin Methods"""
    def is_authenticated(self):
        # TODO
        return None
    def is_active(self):
        # TODO
        return None
    def is_anonymous(self):
        # TODO
        return None
    def get_id(self):
        """Retrieve user's username"""
        return self.username
    def check_password(self, password):
        """Return True if provided password is valid to login"""
        return bcrypt.check_password_hash(self.password, password)

    """Channel Relation Method"""
    def is_subscribing(self, channel):
        return self.subscriptions.filter_by(subscribing_channel_id=channel.channel_id).first() is not None
    def subscribe_to(self, channel):
        if not self.is_subscribing(channel):
            new_subscribing = UserSubscription(subscribers=self, subscribing=channel)
            db.session.add(new_subscribing)
            db.session.commit()
    """YouTube Service Methods"""
    def get_youtube_service(self):
        return helper.build_youtube_service(self.youtube_credentials)
    def insert_video_to_playlist(self, video_id, playlist_id="WL", position=None):
        resource = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                },
                "position": position
            }
        }
        youtube_service = helper.build_youtube_service(self.youtube_credentials)
        return youtube_service.playlistItems().insert(body=resource, part="snippet").execute()

class Subscription(db.Model):
    __tablename__ = "subscription"
    channel_id = db.Column(db.String(30), nullable=False, primary_key=True)
    channel_name = db.Column(db.String(100), nullable=False, server_default=None, unique=False)
    thumbnails_url = db.Column(db.String(200))
    country = db.Column(db.String(5))
    language = db.Column(db.String(5))
    custom_url = db.Column(db.String(100))
    active = db.Column(db.Boolean, nullable=False, server_default=None, unique=False)
    subscribe_datetime = db.Column(db.DateTime, nullable=False, server_default=None, unique=False)
    renew_datetime = db.Column(db.DateTime, nullable=False, server_default=None, unique=False)
    unsubscribe_datetime = db.Column(db.DateTime, nullable=True, server_default=None, unique=False)
    subscribers = db.relationship("UserSubscription",
                                  foreign_keys=[UserSubscription.subscribing_channel_id],
                                  backref=db.backref("subscribing", lazy="joined"),
                                  lazy="dynamic",
                                  cascade="all, delete-orphan")
    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.channel_name = YouTube_Service_Public.channels().list(
            part="snippet",
            id=channel_id
        ).execute()["items"][0]["snippet"]["title"]
        self.activate_response = self.activate()

    def __repr__(self):
        return "<subscription %r>" %self.channel_name

    def activate(self):
        """Activate the Subscription by submitting Hub Subscription"""
        callback_url = url_for("channel_callback_entry", channel_id=self.channel_id, _external=True)
        param_query = urllib.parse.urlencode({"channel_id": self.channel_id})
        topic_url = current_app.config["HUB_YOUTUBE_TOPIC"] + param_query
        response = hub.subscribe(callback_url, topic_url)
        if response.success:
            self.active = True
            self.subscribe_datetime = datetime.now()
            self.renew_datetime = datetime.now()
        return response

    def deactivate(self):
        """Deactivate the Subscription by canceling Hub Subscription"""
        callback_url = url_for("channel_callback_entry", channel_id=self.channel_id, _external=True)
        param_query = urllib.parse.urlencode({"channel_id": self.channel_id})
        topic_url = current_app.config["HUB_YOUTUBE_TOPIC"] + param_query
        response = hub.unsubscribe(callback_url, topic_url)
        if response.success:
            self.active = False
            self.unsubscribe_datetime = datetime.now()
        return response

    def renew_info(self):
        """Update Database Info from YouTube"""
        retrieved_infos = YouTube_Service_Public.channels().list(
            part="snippet",
            id=self.channel_id
        ).execute()["items"][0]
        self.channel_name = retrieved_infos["snippet"]["title"]
        try:
            self.thumbnails_url = retrieved_infos["snippet"]["thumbnails"]["default"]["url"]
        except KeyError:
            pass
        try:
            self.country = retrieved_infos["snippet"]["country"]
        except KeyError:
            pass
        try:
            self.language = retrieved_infos["snippet"]["defaultLanguage"]
        except KeyError:
            pass
        try:
            self.custom_url = retrieved_infos["snippet"]["customUrl"]
        except KeyError:
            pass
        db.session.commit()
        # Consider adding localized infos(?)
        return None

    def renew_hub(self):
        """Renew Subscription by submitting new Hub Subscription"""
        callback_url = url_for("channel_callback_entry", channel_id=self.channel_id, _external=True)
        param_query = urllib.parse.urlencode({"channel_id": self.channel_id})
        topic_url = current_app.config["HUB_YOUTUBE_TOPIC"] + param_query
        response = hub.subscribe(callback_url, topic_url)
        if response.success:
            self.renew_datetime = datetime.now()
        return response

    def renew(self):
        self.renew_info()
        self.renew_hub()

class Callback(db.Model):
    __tablename__ = "callback"
    id = db.Column(db.String(32), nullable=False, primary_key=True)
    received_datetime = db.Column(db.DateTime, nullable=False, server_default=None, unique=False)
    channel_id = db.Column(db.String(30), nullable=False, server_default=None, unique=False)
    action = db.Column(db.String(30), nullable=False, server_default=None, unique=False)
    details = db.Column(db.String(20), nullable=False, server_default=None, unique=False)
    arguments = db.Column(db.JSON, nullable=False, server_default=None, unique=False)
    data = db.Column(db.Text, nullable=False, server_default=None, unique=False)
    user_agent = db.Column(db.String(200), nullable=False, server_default=None, unique=False)
    def __init__(self, received_datetime, channel_id, action, details, arguments, data, user_agent):
        self.id = helper.generate_random_id()
        self.received_datetime = received_datetime
        self.channel_id = channel_id
        self.action = action
        self.details = details
        self.arguments = arguments
        self.data = data
        self.user_agent = user_agent
    def __repr__(self):
        return "<callback %r>" %self.id

class Request(db.Model):
    """
    id                   a unique id for identification
    revieved_datetime    datetime when this request revieved
    method               Type of HTTP request, e.g. "GET", "POST".......etc..
    path                 Paths of Tubee, e.g. "/" for mainpage
    arguments            arguments from GET requests query string as dict
    data                 payload from POST reqests body as dict
    user_agent           can be used to identify hub challenge
    """
    __tablename__ = "request"
    id = db.Column(db.String(32), nullable=False, primary_key=True)
    received_datetime = db.Column(db.DateTime, nullable=False, server_default=None, unique=False)
    method = db.Column(db.String(10), nullable=False, server_default=None, unique=False)
    path = db.Column(db.String(100), nullable=False, server_default=None, unique=False)
    arguments = db.Column(db.JSON, nullable=False, server_default=None, unique=False)
    data = db.Column(db.Text, nullable=False, server_default=None, unique=False)
    user_agent = db.Column(db.String(200), nullable=False, server_default=None, unique=False)
    def __init__(self, method, path, arguments, data, user_agent, received_datetime=datetime.now()):
        self.id = helper.generate_random_id()
        self.received_datetime = received_datetime
        self.method = method
        self.path = path
        self.arguments = arguments
        self.data = data
        self.user_agent = user_agent
    def __repr__(self):
        return "<request %r>" %self.id
    def __str__(self):
        return "Request" + "\n" + \
               str(self.received_datetime) + "\n" + \
               str(self.method) + "\n" + \
               str(self.path) + "\n" + \
               str(self.arguments) + "\n" + \
               str(self.data) + "\n" + \
               str(self.user_agent)

class Notification(db.Model):
    """
    id              a unique id for identification
    initiator       which function/action fired this notification
    send_datetime   dt when this notification fired
    message         content of the notification
    response        recieved resopnse from Pushover Server
    """
    __tablename__ = "notification"
    id = db.Column(db.String(32), nullable=False, primary_key=True)
    initiator = db.Column(db.String(15), nullable=False, server_default=None, unique=False)
    sent_datetime = db.Column(db.DateTime, nullable=False, server_default=None, unique=False)
    message = db.Column(db.String(2000), nullable=False, server_default=None, unique=False)
    kwargs = db.Column(db.JSON, nullable=False, server_default=None, unique=False)
    response = db.Column(db.JSON, nullable=False, server_default=None, unique=False)
    def __init__(self, initiator, message, kwargs, response, sent_datetime=datetime.now()):
        self.id = helper.generate_random_id()
        self.initiator = initiator
        self.sent_datetime = sent_datetime
        self.message = message
        self.kwargs = kwargs
        self.response = response
    def __repr__(self):
        return "<notification %r>" %self.id

class APShedulerJobs(db.Model):
    """A Dummy Model for Flask Migrate"""
    __tablename__ = "apscheduler_jobs"
    id = db.Column(db.String(32), nullable=False, primary_key=True)
    next_run_time = db.Column(db.Float(64), nullable=True, index=True)
    job_state = db.Column(db.LargeBinary, nullable=False)