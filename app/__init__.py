from flask import Flask
import config
from app.routes.forgetpasswordroutes import ForgetPasswordRoutes
from app.routes.logoutroutes import LogoutRoutes
from app.routes.loginroutes import LoginRoutes
from app.routes.registrationroutes import RegistrationRoutes
from app.modals.base_model import create_all


def create_app():
    # Configure Flask to use the `statics` folder for static files
    # and the `templates` folder for templates (both are under app/).
    app = Flask(__name__, static_folder='statics', template_folder='templates')
    # Use configured secret key for session/flash support
    app.secret_key = getattr(config, 'SECRET_KEY', None)

    app.register_blueprint(LoginRoutes().login())
    app.register_blueprint(RegistrationRoutes().registration())
    app.register_blueprint(ForgetPasswordRoutes().forget_password())
    app.register_blueprint(LogoutRoutes().logout())

    # Optionally initialize DB schema on app startup when enabled in config.
    if getattr(config, 'AUTO_INIT_DB', False):
        try:
            create_all()
        except Exception:
            # Fail silently to avoid breaking app start in environments
            # where the database is not yet reachable.
            pass

    return app
