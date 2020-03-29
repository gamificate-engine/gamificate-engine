from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Admin(UserMixin, db.Model):
    id_admin = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    email = db.Column(db.String(128), index=True, unique=True)
    password = db.Column(db.String(128))
    realms = db.relationship('Realm', backref='author', lazy='dynamic')
    # falta premium

    def setPassword(self, password):
        self.password = generate_password_hash(password)

    def checkPassword(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<Admin {}>'.format(self.email)

    def get_id(self):
        return (self.id_admin)


class Realm(db.Model):
    id_realm = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    description = db.Column(db.String(256), unique=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id_admin'))
    badges = db.relationship('Badge', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<Realm {}>'.format(self.name)


class Badge(db.Model):
    id_badge = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    xp = db.Column(db.Integer)
    required = db.Column(db.Integer)
    realm_id = db.Column(db.Integer, db.ForeignKey('realm.id_realm'))
    reward_id = db.Column(db.Integer, db.ForeignKey('reward.id_reward'), nullable=True)

    def __repr__(self):
        return '<Badge {}>'.format(self.name)

class Reward(db.Model):
    id_reward = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    desc = db.Column(db.String(255))

    def __repr__(self):
        return '<Reward {}>'.format(self.name)

# intermediate table between User and Reward
user_reward = db.Table('user_reward',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id_user'), primary_key=True),
    db.Column('reward_id', db.Integer, db.ForeignKey('reward.id_reward'), primary_key=True),
    db.Column('redeem_date', db.DateTime, nullable=True)
)

# intermediate table between User and Badge
user_badge = db.Table('user_badge',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id_user'), primary_key=True),
    db.Column('badge_id', db.Integer, db.ForeignKey('badge.id_badge'), primary_key=True),
    db.Column('progress', db.Integer),
    db.Column('finished', db.Boolean),
    db.Column('finished_date', db.DateTime)
)

class User(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True)
    total_xp = db.Column(db.Integer)
    active = db.Column(db.Boolean)
    level = db.Column(db.Integer)
    realm_id = db.Column(db.Integer, db.ForeignKey('realm.id_realm'))
    badges = db.relationship("Badge", secondary=user_badge)
    rewards = db.relationship("Reward", secondary=user_reward)

    def __repr__(self):
        return '<User {}>'.format(self.email)

class Standings(db.Model):
    realm_id = db.Column(db.Integer, db.ForeignKey('realm.id_realm'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id_realm'), primary_key=True)
    total_xp = db.Column(db.Integer)
    total_badges = db.Column(db.Integer)


class Level(db.Model):
    id_level = db.Column(db.Integer, primary_key=True)
    a = db.Column(db.Integer)
    b = db.Column(db.Integer)
    c = db.Column(db.Integer)
    realm_id = db.Column(db.Integer, db.ForeignKey('realm.id_realm'))

    def __repr__(self):
        return '<Level {}>'.format(self.realm_id)


# User-Loader Function
@login.user_loader
def load_admin(id):
    return Admin.query.get(int(id))
