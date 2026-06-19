from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.modals.applicant_management_model import ApplicantManagementModel
from app.modals.user import UserModel
from app.modals.job_seeker_profile import JobSeekerProfileModel

class ApplicantRoutes:
    def __init__(self):
        self.blueprint = Blueprint("applicant", __name__)

    def applicant_management(self):
        @self.blueprint.route("/employer/applicants", methods=["GET"])
        def list_applicants():
            if "user_id" not in session or session.get("role") != "employer":
                flash("Please log in as an employer.", "error")
                return redirect(url_for("login.index"))

            user_id = session["user_id"]
            
            # Get employer profile
            from app.database import get_connection
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT `Employee_id` FROM `Employee` WHERE `User_id`=%s", (user_id,))
                    employee = cur.fetchone()
                    if not employee:
                        flash("Employer profile not found.", "error")
                        return redirect(url_for("employer.profile"))
                    
                    employee_id = employee['Employee_id']
            finally:
                conn.close()

            applicants = ApplicantManagementModel.get_applications_for_employer(employee_id)
            user_data = UserModel.get_by_id(user_id)
            status_counts = ApplicantManagementModel.get_status_count(employee_id)
            total_applicants = ApplicantManagementModel.get_total_applicants(employee_id)
            
            return render_template(
                "manage_applicants.html", 
                user=user_data, 
                applicants=applicants,
                status_counts=status_counts,
                total_applicants=total_applicants
            )

        @self.blueprint.route("/employer/applicants/<int:job_id>", methods=["GET"])
        def list_job_applicants(job_id):
            if "user_id" not in session or session.get("role") != "employer":
                flash("Please log in as an employer.", "error")
                return redirect(url_for("login.index"))

            applicants = ApplicantManagementModel.get_applications_for_job(job_id)
            user_data = UserModel.get_by_id(session["user_id"])

            return render_template(
                "job_applicants.html", 
                user=user_data, 
                applicants=applicants,
                job_id=job_id
            )

        @self.blueprint.route("/employer/applicant/<int:application_id>", methods=["GET"])
        def view_applicant_detail(application_id):
            if "user_id" not in session or session.get("role") != "employer":
                flash("Please log in as an employer.", "error")
                return redirect(url_for("login.index"))

            applicant = ApplicantManagementModel.get_application_details(application_id)
            if not applicant:
                flash("Application not found.", "error")
                return redirect(url_for("applicant.list_applicants"))

            user_data = UserModel.get_by_id(session["user_id"])

            return render_template(
                "applicant_detail.html", 
                user=user_data, 
                applicant=applicant
            )

        @self.blueprint.route("/employer/applicant/<int:application_id>/status", methods=["POST"])
        def update_applicant_status(application_id):
            if "user_id" not in session or session.get("role") != "employer":
                return jsonify({"status": "error", "message": "Unauthorized"}), 401

            status = request.json.get("status", "").strip()
            valid_statuses = ["pending", "shortlisted", "accepted", "rejected", "under_review"]
            
            if status not in valid_statuses:
                return jsonify({"status": "error", "message": "Invalid status."}), 400

            if ApplicantManagementModel.update_application_status(application_id, status):
                return jsonify({"status": "success", "message": f"Application status updated to {status}."}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to update application status."}), 500

        @self.blueprint.route("/seeker/applications", methods=["GET"])
        def seeker_applications():
            if "user_id" not in session or session.get("role") != "job_seeker":
                flash("Please log in as a job seeker.", "error")
                return redirect(url_for("login.index"))

            user_id = session["user_id"]
            seekers_id = JobSeekerProfileModel.ensure_profile_exists(user_id)
            if not seekers_id:
                flash("Job seeker profile could not be prepared.", "error")
                return redirect(url_for("job_seeker.profile"))
            
            # Get job seeker profile
            from app.database import get_connection
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    # Get all applications for this seeker
                    cur.execute(
                        """
                        SELECT 
                            a.`Application_id`,
                            a.`Job_id`,
                            a.`Status`,
                            a.`Applied_at`,
                            j.`Title` as job_title,
                            j.`Salary`,
                            j.`Location`,
                            e.`Company_name`,
                            e.`Employee_id`
                        FROM `Applications` a
                        JOIN `Jobs` j ON a.`Job_id` = j.`Job_id`
                        JOIN `Employee` e ON j.`Employee_id` = e.`Employee_id`
                        WHERE a.`Seekers_id`=%s
                        ORDER BY a.`Applied_at` DESC
                        """,
                        (seekers_id,)
                    )
                    applications = cur.fetchall()
            finally:
                conn.close()

            user_data = UserModel.get_by_id(user_id)

            return render_template(
                "seeker_applications.html", 
                user=user_data, 
                applications=applications
            )

        return self.blueprint
