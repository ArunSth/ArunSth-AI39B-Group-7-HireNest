from flask import Blueprint
from app.controllers.registrationcontroller import RegistrationController


class RegistrationRoutes:
    def __init__(self):
        self.bp = Blueprint("registration_page", __name__)
        self.controller = RegistrationController()

    def registration(self):
        self.bp.route("/registration",
                      methods=["GET"])(self.controller.registration)
        return self.bp
