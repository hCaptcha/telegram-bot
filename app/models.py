from datetime import datetime

from app.extensions import db


class Channel(db.Model):
    __tablename__ = "channels"

    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(), unique=True, nullable=False)
    restrict = db.Column(db.Boolean)
    name = db.Column(db.String(), nullable=False)

    def __init__(self, chat_id, name, restrict=False):
        self.chat_id = chat_id
        self.name = name
        self.restrict = restrict

    def __repr__(self):
        return "<id {}>".format(self.id)


class Human(db.Model):
    __tablename__ = "humans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(), unique=True, nullable=False)
    user_name = db.Column(db.String(), nullable=False)
    verified = db.Column(db.Boolean)
    attempts = db.Column(db.Integer)
    verification_date = db.Column(db.DateTime)

    def __init__(
        self, user_id, user_name, verified=False, attempts=0, verification_date=None
    ):
        self.user_id = user_id
        self.user_name = user_name
        self.verified = verified
        self.attempts = attempts
        self.verification_date = verification_date

    def __repr__(self):
        return "<id {}>".format(self.id)


class Message(db.Model):
    __tablename__ = "messages"
    __table_args__ = (db.UniqueConstraint("message_id", "chat_id"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(), nullable=False)
    chat_id = db.Column(db.String(), nullable=False)
    message_id = db.Column(db.String(), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, user_id, chat_id, message_id):
        self.user_id = user_id
        self.chat_id = chat_id
        self.message_id = message_id

    def __repr__(self):
        return "<Message {}>".format(self.id)

class Bot(db.Model):
    __tablename__ = "bots"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(), unique=True, nullable=False)
    user_name = db.Column(db.String(), nullable=False)

    def __init__(
        self, user_id, user_name
    ):
        self.user_id = user_id
        self.user_name = user_name

    def __repr__(self):
        return "<Bot {}>".format(self.id)

class HumanChannelMember(db.Model):
    __tablename__ = "humans_channels"

    human_id = db.Column(db.Integer, db.ForeignKey(Human.id), primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey(Channel.id), primary_key=True)

    human = db.relationship('Human', foreign_keys='HumanChannelMember.human_id')
    channel = db.relationship('Channel', foreign_keys='HumanChannelMember.channel_id')

    def __init__(self, human_id, channel_id):
        self.human_id = human_id
        self.channel_id = channel_id

    def __repr__(self):
        return "<HumanChannelMember (human_id: {}, channel_id: {})>".format(self.human_id, self.channel_id)

class BotChannelMember(db.Model):
    __tablename__ = "bots_channels"

    bot_id = db.Column(db.Integer, db.ForeignKey(Bot.id), primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey(Channel.id), primary_key=True)

    bot = db.relationship('Bot', foreign_keys='BotChannelMember.bot_id')
    channel = db.relationship('Channel', foreign_keys='BotChannelMember.channel_id')

    def __init__(self, bot_id, channel_id):
        self.bot_id = human_id
        self.channel_id = channel_id

    def __repr__(self):
        return "<BotChannelMember (bot_id: {}, channel_id: {})>".format(self.bot_id, self.channel_id)
