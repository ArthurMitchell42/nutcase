# from datetime import datetime
# from hashlib import md5
# from time import time
# from werkzeug.security import generate_password_hash, check_password_hash
# import jwt
# from flask import current_app
# from flask_login import UserMixin
# from app import db
# from app import login

# class User(UserMixin, db.Model):
#     id              = db.Column(db.Integer, primary_key=True)
#     username        = db.Column(db.String(64), index=True, unique=True)
#     email           = db.Column(db.String(120), index=True, unique=True)
#     password_hash   = db.Column(db.String(128))
#     last_seen       = db.Column(db.DateTime, default=datetime.utcnow)
#     group           = db.Column(db.String(128))
#     login_method    = db.Column(db.String(128), default='local')
#     ui_theme        = db.Column(db.String(64))
#     must_change_pw  = db.Column(db.Boolean, default=True)

#     def __repr__(self):
#         return '<User {}>'.format(self.username)

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)

#     def get_avatar(self, size):
#         digest = md5(self.email.lower().encode('utf-8')).hexdigest()
#         return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

#     def is_admin(self):
#         if self.group == None:
#             return False
#         if self.group.lower() == 'admin':
#             return True
#         return False

#     def is_local(self):
#         if self.login_method == None:
#             return True
#         if self.login_method.lower() == 'local':
#             return True
#         return False

#     def get_reset_password_token(self, expires_in=600):
#         return jwt.encode(
#             {'reset_password': self.id, 'exp': time() + expires_in},
#             current_app.config['SECRET_KEY'], algorithm='HS256')

#     @staticmethod
#     def verify_reset_password_token(token):
#         try:
#             id = jwt.decode(token, current_app.config['SECRET_KEY'],
#                             algorithms=['HS256'])['reset_password']
#         except:
#             return
#         return User.query.get(id)

# @login.user_loader
# def load_user(id):
#     return User.query.get(int(id))
