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
