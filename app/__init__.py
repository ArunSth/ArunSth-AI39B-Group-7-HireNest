from flask import Flask
import config
from app.routes.forgetpasswordroutes import ForgetPasswordRoutes
from app.routes.logoutroutes import LogoutRoutes
from app.routes.loginroutes import LoginRoutes
from app.routes.registrationroutes import RegistrationRoutes


def create_app():
    # Configure Flask to use the `statics` folder for static files
    # and the `templates` folder for templates (both are under app/).
    app = Flask(__name__, static_folder='statics', template_folder='templates')

    app.register_blueprint(LoginRoutes().login())
    app.register_blueprint(RegistrationRoutes().registration())
    app.register_blueprint(ForgetPasswordRoutes().forget_password())
    app.register_blueprint(LogoutRoutes().logout())

    return app
