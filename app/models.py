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
    realms = db.relationship('Realm', lazy='dynamic', cascade="delete")
    subscription_key = db.Column(db.String(128), unique=True)

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
    name = db.Column(db.String(32))
    description = db.Column(db.String(256))
    id_admin = db.Column(db.Integer, db.ForeignKey('gamificate.admin.id_admin'))
    badges = db.relationship('Badge', lazy='dynamic', cascade="delete")
    users = db.relationship('User', lazy='dynamic', cascade="delete, save-update")
    rewards = db.relationship('Reward', lazy='dynamic', cascade="delete")
    api_key = db.Column(db.String(128), unique=True)
    a = db.Column(db.Float)
    b = db.Column(db.Float)
    active = db.Column(db.Boolean, default=True)

    def xp_required(self,lvl):
        required = self.a * lvl**2 + self.b * lvl
        return required

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
    description = db.Column(db.String(256))
    xp = db.Column(db.Integer)
    required = db.Column(db.Integer)
    image_url = db.Column(db.String(2000))
    id_realm = db.Column(db.Integer, db.ForeignKey('gamificate.realm.id_realm'))
    id_reward = db.Column(db.Integer, db.ForeignKey('gamificate.reward.id_reward', ondelete="SET NULL"), nullable=True)

    def __repr__(self):
        return '<Badge {}>'.format(self.name)

    def to_dict(self):
        data = {
            'id_badge': self.id_badge,
            'name': self.name,
            'description': self.description,
            'xp': self.xp,
            'required': self.required,
            'id_realm': self.id_realm
        }
        if self.image_url:
            data['image_url'] = self.image_url

        if self.id_reward:
            data['id_reward'] = self.id_reward
        
        return data

    def new_or_update(self, data):
        for field in ['name', 'description', 'xp', 'required', 'image_url', 'id_reward']:
            if field in data:
                setattr(self, field, data[field])


class Reward(db.Model):
    __tablename__ = 'reward'
    __table_args__ = {'schema': 'gamificate'}
    id_reward = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    desc = db.Column(db.String(256))
    id_realm = db.Column(db.Integer, db.ForeignKey('gamificate.realm.id_realm'))

    def __repr__(self):
        return '<Reward {}>'.format(self.name)

    def to_dict(self):
        data = {
            'id_reward': self.id_reward,
            'name': self.name,
            'description': self.desc,
            'id_realm': self.id_realm
        }
        return data

    def from_dict(self, data):
        for field in ['name', 'desc']:
            if field in data:
                setattr(self, field, data[field])

class UserRewards(db.Model):
    __table_args__ = {'schema': 'gamificate'}
    __tablename__ = 'user_reward'
    id_user = db.Column(db.Integer, db.ForeignKey('gamificate.user.id_user'), primary_key=True)
    id_reward = db.Column(db.Integer, db.ForeignKey('gamificate.reward.id_reward'), primary_key=True)
    redeem_date = db.Column(db.DateTime, nullable=True)
    reward = db.relationship("Reward")

    def redeem(self, reward):
        self.redeem_date = datetime.now()
        self.reward = reward

    def to_dict(self):
        data = {
            'id_reward': self.reward.id_reward,
            'id_user': self.id_user,
            'redeem_date': self.redeem_date,
            'reward_name': self.reward.name
        }
        return data


class UserBadges(db.Model):
    __tablename__ = 'user_badge'
    __table_args__ = {'schema': 'gamificate'}
    id_user = db.Column(db.Integer, db.ForeignKey('gamificate.user.id_user'), primary_key=True)
    id_badge = db.Column(db.Integer, db.ForeignKey('gamificate.badge.id_badge'), primary_key=True)
    progress = db.Column(db.Integer)
    finished = db.Column(db.Boolean)
    finished_date = db.Column(db.DateTime)
    badge = db.relationship("Badge")

    def update_progress(self, progress, badge, user, realm):
        self.progress = self.progress + progress

        if self.progress >= badge.required:
            self.finished = True
            self.finished_date = datetime.now()
            user.total_xp = user.total_xp + badge.xp
            user.total_badges = user.total_badges + 1

            lvl = user.level
            while realm.xp_required(lvl) < user.total_xp:
                lvl = lvl + 1
            if lvl > user.level:
                user.level = lvl

    def to_dict(self):
        data = {
            'id_badge': self.badge.id_badge,
            'progress': self.progress,
            'finished': self.finished,
            'required': self.badge.required
        }
        if self.finished:
            data['finished_date'] = self.finished_date
        return data


class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'gamificate'}
    id_user = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(254))
    total_xp = db.Column(db.Integer)
    total_badges = db.Column(db.Integer)
    active = db.Column(db.Boolean)
    level = db.Column(db.Integer)
    id_realm = db.Column(db.Integer, db.ForeignKey('gamificate.realm.id_realm'))
    badges = db.relationship("UserBadges", lazy='dynamic', cascade="delete")
    rewards = db.relationship("UserRewards", lazy='dynamic', cascade="delete")

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

    def rank_to_dict(self, rank):
        data = {
            'rank': rank,
            'id_user': self.id_user,
            'username': self.username,
            'level': self.level,
            'total_xp': self.total_xp,
            'total_badges': self.total_badges
        }
        return data


class Standings(db.Model):
    __tablename__ = 'standings'
    __table_args__ = {'schema': 'gamificate'}
    realm_id = db.Column(db.Integer, db.ForeignKey('gamificate.realm.id_realm'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('gamificate.user.id_user'), primary_key=True)
    total_xp = db.Column(db.Integer)
    total_badges = db.Column(db.Integer)

# User-Loader Function
@login.user_loader
def load_admin(id):
    return Admin.query.get(int(id))
