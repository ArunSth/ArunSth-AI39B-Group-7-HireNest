from flask import Flask
import config
from app.routes.forgetpasswordroutes import ForgetPasswordRoutes
from app.routes.logoutroutes import LogoutRoutes
from app.routes.loginroutes import LoginRoutes
from app.routes.registrationroutes import RegistrationRoutes
from app.modals.base_model import create_all, run_migrations
from app.routes.job_seeker_routes import JobSeekerRoutes
from app.routes.employer_routes import EmployerRoutes
from app.routes.job_posting_routes import JobPostingRoutes
from app.routes.applicant_routes import ApplicantRoutes
from app.routes.interview_routes import InterviewRoutes


def create_app():
    app = Flask(__name__, static_folder='statics', template_folder='templates')
    app.secret_key = getattr(config, 'SECRET_KEY', None)
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_HTTPONLY'] = True

    app.register_blueprint(LoginRoutes().login())
    app.register_blueprint(RegistrationRoutes().registration())
    app.register_blueprint(ForgetPasswordRoutes().forget_password())
    app.register_blueprint(LogoutRoutes().logout())
    
    # Register job seeker routes (dashboard and profile)
    job_seeker_routes = JobSeekerRoutes()
    app.register_blueprint(job_seeker_routes.register_routes())
    
    # Register employer routes (dashboard and profile)
    employer_routes = EmployerRoutes()
    app.register_blueprint(employer_routes.register_routes())

    from flask import send_from_directory
    import os

    @app.route('/uploads/<path:filename>')
    def download_file(filename):
        return send_from_directory(os.path.join(app.root_path, '..', 'uploads'), filename)

    if getattr(config, 'AUTO_INIT_DB', False):
        try:
            create_all()
            run_migrations()
        except Exception:
            pass

    return app