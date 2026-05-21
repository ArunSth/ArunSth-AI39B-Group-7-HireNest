from flask import Blueprint
from app.controllers.logincontroller import LoginController


class LoginRoutes:
    def __init__(self):
        self.bp = Blueprint("login_page", __name__)
        self.controller = LoginController()

    def login(self):
        self.bp.route("/", methods=["GET"])(self.controller.login)
        self.bp.route("/home", methods=["GET"])(self.controller.login)
        self.bp.route("/login", methods=["GET"])(self.controller.login)
        return self.bp
