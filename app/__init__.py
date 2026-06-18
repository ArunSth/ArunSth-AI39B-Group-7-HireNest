from flask import Flask, send_from_directory
import os
import config

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.routes.forgetpasswordroutes import ForgetPasswordRoutes
from app.routes.logoutroutes import LogoutRoutes
from app.routes.loginroutes import LoginRoutes
from app.routes.registrationroutes import RegistrationRoutes
from app.routes.job_seeker_routes import JobSeekerRoutes
from app.routes.employer_routes import EmployerRoutes
from app.routes.job_posting_routes import JobPostingRoutes
from app.routes.applicant_routes import ApplicantRoutes
from app.routes.interview_routes import InterviewRoutes
from app.routes.messageroutes import MessageRoutes
from app.routes.notificationroutes import NotificationRoutes
from app.routes.job_alert_routes import JobAlertRoutes
from app.routes.review_routes import ReviewRoutes
from app.routes.subscription_routes import SubscriptionRoutes

from app.routes.admin_routes import AdminRoutes

def create_app():
    app = Flask(__name__, static_folder='statics', template_folder='templates')

    # 🔥 LOAD CONFIG (VERY IMPORTANT)
    app.config.from_object(config.Config)

    # Secret key
    app.secret_key = getattr(config, 'SECRET_KEY', None)

    # Session config
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_HTTPONLY'] = True

    # 🔥 INIT DATABASE (THIS WAS MISSING)
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(LoginRoutes().login())
    app.register_blueprint(RegistrationRoutes().registration())
    app.register_blueprint(ForgetPasswordRoutes().forget_password())
    app.register_blueprint(LogoutRoutes().logout())
    app.register_blueprint(JobSeekerRoutes().register_routes())
    app.register_blueprint(EmployerRoutes().employer_profile())
    app.register_blueprint(JobPostingRoutes().job_posting())
    app.register_blueprint(ApplicantRoutes().applicant_management())
    app.register_blueprint(InterviewRoutes().interview_scheduling())
    app.register_blueprint(MessageRoutes().messages())
    app.register_blueprint(NotificationRoutes().notifications())
    app.register_blueprint(JobAlertRoutes().job_alerts())
    app.register_blueprint(ReviewRoutes().review_routes())
    app.register_blueprint(SubscriptionRoutes().subscription_routes())

    # Upload route
    app.register_blueprint(AdminRoutes().register_routes())
    
    from flask import send_from_directory
    import os

    @app.route('/uploads/<path:filename>')
    def download_file(filename):
        return send_from_directory(
            os.path.join(app.root_path, '..', 'uploads'),
            filename
        )

    # 🔥 AUTO DB INIT (SAFE VERSION)
    if getattr(config, 'AUTO_INIT_DB', False):
        with app.app_context():
            try:
                from app.modals.base_model import create_all, run_migrations
                create_all()
                run_migrations()
            except Exception as e:
                print("DB INIT ERROR:", e)

    return app