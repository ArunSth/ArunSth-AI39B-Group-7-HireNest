from flask import Blueprint
from app.controllers.logoutcontroller import LogoutController


class LogoutRoutes:
    def __init__(self):
        self.bp = Blueprint("logout_page", __name__)
        self.controller = LogoutController()

    def logout(self):
        self.bp.route("/logout", methods=["GET"])(self.controller.logout)
        return self.bp
