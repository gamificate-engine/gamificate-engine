from app import app, db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
from datetime import datetime
import jwt


class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    __table_args__ = {'schema': 'gamificate'}
    id_admin = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    email = db.Column(db.String(128), index=True, unique=True)
    password = db.Column(db.String(128))
    premium = db.Column(db.Boolean, default=False)
    realms = db.relationship('Realm', lazy='dynamic')

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id_admin, 'exp': time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return

        return Admin.query.get(id)

    def setPassword(self, password):
        self.password = generate_password_hash(password)

    def checkPassword(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<Admin {}>'.format(self.email)

    def get_id(self):
        return (self.id_admin)


class Realm(db.Model):
    __tablename__ = 'realm'
    __table_args__ = {'schema': 'gamificate'}
    id_realm = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    description = db.Column(db.String(256))
    admin_id = db.Column(db.Integer, db.ForeignKey('gamificate.admin.id_admin'))
    badges = db.relationship('Badge', lazy='dynamic')
    users = db.relationship('User', lazy='dynamic')
    rewards = db.relationship('Reward', lazy='dynamic')
    api_key = db.Column(db.String(128), unique=True)
    a = db.Column(db.Float)
    b = db.Column(db.Float)
    

    def set_api_key(self, api_key):
        self.api_key = generate_password_hash(api_key)

    def check_api_key(self, api_key):
        return check_password_hash(self.api_key, api_key)

    def __repr__(self):
        return '<Realm {}>'.format(self.name)    


class Badge(db.Model):
    __tablename__ = 'badge'
    __table_args__ = {'schema': 'gamificate'}
    id_badge = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    xp = db.Column(db.Integer)
    required = db.Column(db.Integer)
    id_realm = db.Column(db.Integer, db.ForeignKey('gamificate.realm.id_realm'))
    id_reward = db.Column(db.Integer, db.ForeignKey(
        'gamificate.reward.id_reward'), nullable=True)

    def __repr__(self):
        return '<Badge {}>'.format(self.name)

    def to_dict(self):
        data = {
            'id_badge': self.id_badge,
            'name': self.name,
            'xp': self.xp,
            'required': self.required,
            'id_realm': self.id_realm
        }
        if self.id_reward:
            data['id_reward'] = self.id_reward
        return data

    def new_or_update(self, data):
        for field in ['name', 'xp', 'required', 'id_reward']:
            if field in data:
                setattr(self, field, data[field])


class Reward(db.Model):
    __tablename__ = 'reward'
    __table_args__ = {'schema': 'gamificate'}
    id_reward = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    desc = db.Column(db.String(255))
    id_realm = db.Column(db.Integer, db.ForeignKey('gamificate.realm.id_realm'))

    def __repr__(self):
        return '<Reward {}>'.format(self.name)

# intermediate table between User and Reward


class UserRewards(db.Model):
    __table_args__ = {'schema': 'gamificate'}
    __tablename__ = 'user_reward'
    id_user = db.Column(db.Integer, db.ForeignKey(
        'gamificate.user.id_user'), primary_key=True)
    id_reward = db.Column(db.Integer, db.ForeignKey(
        'gamificate.reward.id_reward'), primary_key=True)
    redeem_date = db.Column(db.DateTime, nullable=True)
    reward = db.relationship("Reward")

    def redeem(self, reward):
        self.redeem_date = datetime.now()
        self.reward = reward

    def to_dict(self):
        data = {
            'id_reward': self.id_reward,
            'redeem_date': self.redeem_date
        }
        return data

# intermediate table between User and Badge


class UserBadges(db.Model):
    __tablename__ = 'user_badge'
    __table_args__ = {'schema': 'gamificate'}
    id_user = db.Column(db.Integer, db.ForeignKey(
        'gamificate.user.id_user'), primary_key=True)
    id_badge = db.Column(db.Integer, db.ForeignKey(
        'gamificate.badge.id_badge'), primary_key=True)
    progress = db.Column(db.Integer)
    finished = db.Column(db.Boolean)
    finished_date = db.Column(db.DateTime)
    badge = db.relationship("Badge")

    def update_progress(self, progress, badge, user):
        self.progress = self.progress + progress

        if self.progress >= badge.required:
            self.finished = True
            self.finished_date = datetime.now()
            user.total_xp = user.total_xp + badge.xp
            user.total_badges = user.total_badges + 1

    def to_dict(self):
        data = {
            'id_badge': self.id_badge,
            'progress': self.progress,
            'finished': self.finished
        }
        if self.finished:
            data['finished_date'] = self.finished_date
        return data


class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'gamificate'}
    id_user = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(254), unique=True)
    total_xp = db.Column(db.Integer)
    total_badges = db.Column(db.Integer)
    active = db.Column(db.Boolean)
    level = db.Column(db.Integer)
    id_realm = db.Column(db.Integer, db.ForeignKey('gamificate.realm.id_realm'))
    badges = db.relationship("UserBadges", lazy='dynamic')
    rewards = db.relationship("UserRewards", lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def to_dict(self, include_email=True):
        data = {
            'id': self.id_user,
            'username': self.username,
            'total_xp': self.total_xp,
            'total_badges': self.total_badges,
            'active': self.active,
            'level': self.level,
            'id_realm': self.id_realm
        }
        if include_email:
            data['email'] = self.email

        return data

    def from_dict(self, data):
        for field in ['username', 'email', 'active']:
            if field in data:
                setattr(self, field, data[field])

    def new_user(self, data):
        self.username = data['username']
        self.email = data['email']
        self.total_xp = 0
        self.total_badges = 0
        self.active = True
        self.level = 1

    def rank_to_dict(self, rank, field):
        data = {
            'rank': rank,
            'id_user': self.id_user,
            'username': self.username
        }
        data[field] = getattr(self, field)
        return data


class Standings(db.Model):
    __tablename__ = 'standings'
    __table_args__ = {'schema': 'gamificate'}
    realm_id = db.Column(db.Integer, db.ForeignKey(
        'gamificate.realm.id_realm'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'gamificate.user.id_user'), primary_key=True)
    total_xp = db.Column(db.Integer)
    total_badges = db.Column(db.Integer)



# User-Loader Function
@login.user_loader
def load_admin(id):
    return Admin.query.get(int(id))
