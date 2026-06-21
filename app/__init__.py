from app.routes.skill_assessment_routes import SkillAssessmentRoutes
from app.routes.application_tracking_routes import ApplicationTrackingRoutes
from flask import Flask, send_from_directory  # Remove 'app' - it's not a Flask export
import os
import config

from flask_mail import Mail

mail = Mail()

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
from app.routes.seeker_job_routes import SeekerJobRoutes

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

    # 🔥 INIT MAIL
    mail.init_app(app)

    # Register Blueprints
    app.register_blueprint(LoginRoutes().login())
    app.register_blueprint(RegistrationRoutes().registration())
    app.register_blueprint(ForgetPasswordRoutes().forget_password())
    app.register_blueprint(LogoutRoutes().logout())
    app.register_blueprint(JobSeekerRoutes().register_routes())
    app.register_blueprint(SeekerJobRoutes().register_routes())
    app.register_blueprint(EmployerRoutes().employer_profile())
    app.register_blueprint(JobPostingRoutes().job_posting())
    app.register_blueprint(ApplicantRoutes().applicant_management())
    app.register_blueprint(InterviewRoutes().interview_scheduling())
    app.register_blueprint(MessageRoutes().messages())
    app.register_blueprint(NotificationRoutes().notifications())
    app.register_blueprint(JobAlertRoutes().job_alerts())
    app.register_blueprint(ReviewRoutes().review_routes())
    app.register_blueprint(SubscriptionRoutes().subscription_routes())
    app.register_blueprint(SkillAssessmentRoutes().register_routes())
    app.register_blueprint(ApplicationTrackingRoutes().register_routes())
    
    # Upload route
    app.register_blueprint(AdminRoutes().register_routes())
    
    # ── Load Admin Settings from DB into app.config ──────────
    with app.app_context():
        try:
            from app.database import get_connection
            conn = get_connection()
            with conn.cursor() as cur:

                # Auto-create table if it doesn't exist
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS `AdminSettings` (
                        `key` VARCHAR(50) PRIMARY KEY,
                        `value` VARCHAR(255) NOT NULL
                    )
                """)

                # Insert defaults if table is empty
                cur.execute("SELECT COUNT(*) as count FROM `AdminSettings`")
                row = cur.fetchone()
                if row['count'] == 0:
                    cur.executemany(
                        "INSERT INTO `AdminSettings` (`key`, `value`) VALUES (%s, %s)",
                        [
                            ('userRegistration',     '1'),
                            ('employerVerification', '0'),
                            ('autoApproveJobs',      '0'),
                            ('jobModeration',        '1'),
                            ('emailAlerts',          '1'),
                            ('weeklyReports',        '0'),
                        ]
                    )

                conn.commit()

                # Now load them
                cur.execute("SELECT `key`, `value` FROM `AdminSettings`")
                rows = cur.fetchall()

            conn.close()

            saved = {row['key']: row['value'] == '1' for row in rows}
            app.config['ADMIN_SETTINGS'] = {
                'userRegistration':     saved.get('userRegistration',     True),
                'employerVerification': saved.get('employerVerification', False),
                'autoApproveJobs':      saved.get('autoApproveJobs',      False),
                'jobModeration':        saved.get('jobModeration',        True),
                'emailAlerts':          saved.get('emailAlerts',          True),
                'weeklyReports':        saved.get('weeklyReports',        False),
            }
            print("✅ Admin settings loaded from DB")

        except Exception as e:
            app.config['ADMIN_SETTINGS'] = {
                'userRegistration':     True,
                'employerVerification': False,
                'autoApproveJobs':      False,
                'jobModeration':        True,
                'emailAlerts':          True,
                'weeklyReports':        False,
            }
            print(f"⚠️ Admin settings defaulted: {e}")
    # ─────────────────────────────────────────────────────────
    
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
                from app.modals.base_model import create_all, run_migrations, seed_admin
                create_all()
                run_migrations()
                from app.modals.skill_assessment_model import SkillAssessmentModel
                SkillAssessmentModel.seed_default_assessments()
                seed_admin()
            except Exception as e:
                print("DB INIT ERROR:", e)

    return app
