from flask import Blueprint
from app.controllers.forgetpasswordcontroller import ForgetpasswordController


class ForgetPasswordRoutes:
    def __init__(self):
        self.bp = Blueprint("forget_password_page", __name__)
        self.controller = ForgetpasswordController()

    def forget_password(self):
        self.bp.route(
            "/forgetpassword", methods=["GET"], endpoint="forget_password")(self.controller.password)
        return self.bp
