from run import db

""" User model for storing user details"""


class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
