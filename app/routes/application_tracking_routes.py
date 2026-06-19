"""
Application Tracking Routes  (Feature 09)
=========================================
Adds the missing pieces of the Job-Seeker side application-tracking
flow on top of the existing applicant_routes.py:

URL Map
-------
GET   /seeker/applications/track                 -> rich tracking dashboard
GET   /seeker/applications/<application_id>      -> single application details + timeline
POST  /seeker/applications/<application_id>/withdraw
                                                 -> withdraw application (only if still open)
GET   /seeker/applications/status-feed           -> JSON polling endpoint for real-time
                                                    status updates (used by the UI)

It does NOT touch the existing /seeker/applications route in
applicant_routes.py -- it complements it.
"""

from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, jsonify
)

from app.database import get_connection
from app.modals.user import UserModel
from app.modals.job_seeker_profile import JobSeekerProfileModel
from app.modals.applicant_management_model import ApplicantManagementModel
from app.modals.notification import NotificationModel


# Allowed status values the seeker can see / move to
VALID_STATUSES = [
    "pending", "under_review", "shortlisted",
    "accepted", "rejected", "hired", "withdrawn"
]


class ApplicationTrackingRoutes:
    def __init__(self):
        self.blueprint = Blueprint("application_tracking", __name__)

    # ------------------------------------------------------------------
    #  Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _require_seeker():
        if "user_id" not in session or session.get("role") != "job_seeker":
            return None, None
        user_id = session["user_id"]
        JobSeekerProfileModel.ensure_profile_exists(user_id)
        profile = JobSeekerProfileModel.get_profile_by_user_id(user_id)
        if not profile:
            return user_id, None
        return user_id, profile["Seekers_id"]

    @staticmethod
    def _get_seeker_applications(seekers_id):
        """Detailed list of applications for the tracking dashboard."""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT  a.`Application_id`, a.`Job_id`, a.`Status`,
                            a.`Applied_at`, a.`Cover_letter`,
                            j.`Title`        AS job_title,
                            j.`Salary`,
                            j.`Location`,
                            j.`Status`       AS job_status,
                            e.`Company_name`,
                            e.`Employee_id`,
                            (SELECT MAX(i.`Interview_date`) FROM `Interview` i
                              WHERE i.`Application_id` = a.`Application_id`) AS next_interview_date,
                            (SELECT MAX(i.`Interview_time`) FROM `Interview` i
                              WHERE i.`Application_id` = a.`Application_id`) AS next_interview_time
                    FROM    `Applications` a
                    JOIN    `Jobs` j ON a.`Job_id` = j.`Job_id`
                    JOIN    `Employee` e ON j.`Employee_id` = e.`Employee_id`
                    WHERE   a.`Seekers_id` = %s
                    ORDER BY a.`Applied_at` DESC
                    """,
                    (seekers_id,),
                )
                return cur.fetchall() or []
        finally:
            conn.close()

    @staticmethod
    def _get_application_for_seeker(application_id, seekers_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT  a.*, j.`Title` AS job_title, j.`Salary`,
                            j.`Location`, j.`Description` AS job_description,
                            j.`Status` AS job_status,
                            e.`Company_name`, e.`Employee_id`, e.`Logo`
                    FROM    `Applications` a
                    JOIN    `Jobs` j ON a.`Job_id` = j.`Job_id`
                    JOIN    `Employee` e ON j.`Employee_id` = e.`Employee_id`
                    WHERE   a.`Application_id` = %s AND a.`Seekers_id` = %s
                    """,
                    (application_id, seekers_id),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def _status_counts(seekers_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT LOWER(`Status`) AS status, COUNT(*) AS cnt
                    FROM   `Applications`
                    WHERE  `Seekers_id` = %s
                    GROUP BY LOWER(`Status`)
                    """,
                    (seekers_id,),
                )
                rows = cur.fetchall() or []
                counts = {s: 0 for s in VALID_STATUSES}
                total = 0
                for r in rows:
                    s = (r["status"] or "pending").lower()
                    counts[s] = counts.get(s, 0) + r["cnt"]
                    total += r["cnt"]
                counts["total"] = total
                return counts
        finally:
            conn.close()

    # ------------------------------------------------------------------
    #  Route registration
    # ------------------------------------------------------------------
    def register_routes(self):

        # 1) Rich tracking dashboard
        @self.blueprint.route("/seeker/applications/track", methods=["GET"])
        def track():
            user_id, seekers_id = self._require_seeker()
            if not user_id:
                flash("Please log in as a job seeker.", "error")
                return redirect(url_for("login.index"))
            if not seekers_id:
                flash("Please complete your job seeker profile first.", "error")
                return redirect(url_for("job_seeker.profile"))

            applications = self._get_seeker_applications(seekers_id)
            counts = self._status_counts(seekers_id)
            user_data = UserModel.get_by_id(user_id)

            return render_template(
                "application_tracking.html",
                user=user_data,
                applications=applications,
                counts=counts,
            )

        # 2) Detail page (timeline view)
        @self.blueprint.route("/seeker/applications/<int:application_id>",
                              methods=["GET"])
        def detail(application_id):
            user_id, seekers_id = self._require_seeker()
            if not user_id:
                flash("Please log in as a job seeker.", "error")
                return redirect(url_for("login.index"))
            if not seekers_id:
                flash("Please complete your job seeker profile first.", "error")
                return redirect(url_for("job_seeker.profile"))

            application = self._get_application_for_seeker(application_id, seekers_id)
            if not application:
                flash("Application not found.", "error")
                return redirect(url_for("application_tracking.track"))

            # Pull interviews tied to this application (if any)
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT * FROM `Interview`
                        WHERE `Application_id` = %s
                        ORDER BY `Interview_date` DESC, `Interview_time` DESC
                        """,
                        (application_id,),
                    )
                    interviews = cur.fetchall() or []
            finally:
                conn.close()

            return render_template(
                "application_detail_tracking.html",
                user=UserModel.get_by_id(user_id),
                application=application,
                interviews=interviews,
                valid_statuses=VALID_STATUSES,
            )

        # 3) Withdraw an application
        @self.blueprint.route("/seeker/applications/<int:application_id>/withdraw",
                              methods=["POST"])
        def withdraw(application_id):
            user_id, seekers_id = self._require_seeker()
            if not user_id:
                if request.is_json:
                    return jsonify({"status": "error",
                                    "message": "Unauthorized"}), 401
                flash("Please log in as a job seeker.", "error")
                return redirect(url_for("login.index"))
            if not seekers_id:
                if request.is_json:
                    return jsonify({"status": "error",
                                    "message": "Profile required"}), 400
                flash("Please complete your job seeker profile first.", "error")
                return redirect(url_for("job_seeker.profile"))

            application = self._get_application_for_seeker(application_id, seekers_id)
            if not application:
                if request.is_json:
                    return jsonify({"status": "error",
                                    "message": "Application not found"}), 404
                flash("Application not found.", "error")
                return redirect(url_for("application_tracking.track"))

            current_status = (application.get("Status") or "").lower()
            # Acceptance Criteria: withdraw only if position is still open
            if current_status in ("rejected", "hired", "withdrawn"):
                msg = ("This application can no longer be withdrawn "
                       "because it is already closed.")
                if request.is_json:
                    return jsonify({"status": "error", "message": msg}), 400
                flash(msg, "error")
                return redirect(url_for("application_tracking.detail",
                                        application_id=application_id))

            ok = ApplicantManagementModel.update_application_status(
                application_id, "withdrawn"
            )
            if not ok:
                if request.is_json:
                    return jsonify({"status": "error",
                                    "message": "Could not withdraw"}), 500
                flash("Could not withdraw your application. Please try again.", "error")
                return redirect(url_for("application_tracking.detail",
                                        application_id=application_id))

            # Notify the employer that the candidate withdrew (best-effort)
            try:
                conn = get_connection()
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            SELECT e.`User_id` AS emp_user_id
                            FROM `Applications` a
                            JOIN `Jobs` j ON a.`Job_id` = j.`Job_id`
                            JOIN `Employee` e ON j.`Employee_id` = e.`Employee_id`
                            WHERE a.`Application_id` = %s
                            """,
                            (application_id,),
                        )
                        row = cur.fetchone()
                finally:
                    conn.close()
                if row and row.get("emp_user_id"):
                    NotificationModel.create_notification(
                        user_id=row["emp_user_id"],
                        title="Candidate Withdrew",
                        message=(f"A candidate withdrew their application for "
                                 f"'{application.get('job_title','your job')}'."),
                        notification_type="application",
                        reference_id=application_id,
                    )
            except Exception as e:
                print(f"[application_tracking.withdraw] notify employer failed: {e}")

            if request.is_json:
                return jsonify({"status": "success",
                                "message": "Application withdrawn."}), 200
            flash("Application withdrawn successfully.", "success")
            return redirect(url_for("application_tracking.track"))

        # 4) JSON polling feed for real-time UI updates
        @self.blueprint.route("/seeker/applications/status-feed", methods=["GET"])
        def status_feed():
            user_id, seekers_id = self._require_seeker()
            if not user_id or not seekers_id:
                return jsonify({"status": "error",
                                "message": "Unauthorized"}), 401
            try:
                conn = get_connection()
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            SELECT a.`Application_id`, a.`Status`,
                                   a.`Applied_at`, j.`Title` AS job_title,
                                   e.`Company_name`
                            FROM   `Applications` a
                            JOIN   `Jobs` j ON a.`Job_id` = j.`Job_id`
                            JOIN   `Employee` e ON j.`Employee_id` = e.`Employee_id`
                            WHERE  a.`Seekers_id` = %s
                            ORDER BY a.`Applied_at` DESC
                            """,
                            (seekers_id,),
                        )
                        rows = cur.fetchall() or []
                finally:
                    conn.close()

                # serialise dates / decimals
                feed = []
                for r in rows:
                    feed.append({
                        "application_id": r["Application_id"],
                        "status": r["Status"],
                        "job_title": r["job_title"],
                        "company_name": r["Company_name"],
                        "applied_at": (r["Applied_at"].isoformat()
                                       if r.get("Applied_at") else None),
                    })
                return jsonify({"status": "success",
                                "data": feed,
                                "server_time": datetime.utcnow().isoformat()}), 200
            except Exception as e:
                print(f"[application_tracking.status_feed] {e}")
                return jsonify({"status": "error",
                                "message": "Could not load feed"}), 500

        return self.blueprint
