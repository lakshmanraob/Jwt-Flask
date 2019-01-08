from flask import jsonify


class UserRegister:
    def __init__(self, username, password):
        self.usermodel = UserModel(username, password)

    def display(self):
        return print("lakshman")


class UserModel:
    def __init__(self, username, password):
        self.username = username
        self.password = password
