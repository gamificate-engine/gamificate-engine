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
    # falta rewards



# User-Loader Function
@login.user_loader
def load_admin(id):
    return Admin.query.get(int(id))