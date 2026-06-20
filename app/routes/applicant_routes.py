from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.controllers.notification_controller import NotificationController
from app.modals.applicant_management_model import ApplicantManagementModel
from app.modals.job_posting_model import JobPostingModel
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
                    cur.execute(
                        "SELECT `Employee_id` FROM `Employee` WHERE `User_id`=%s", (user_id,))
                    employee = cur.fetchone()
                    if not employee:
                        flash("Employer profile not found.", "error")
                        return redirect(url_for("employer.profile"))

                    employee_id = employee['Employee_id']
            finally:
                conn.close()

            applicants = ApplicantManagementModel.get_applications_for_employer(
                employee_id)
            user_data = UserModel.get_by_id(user_id)
            status_counts = ApplicantManagementModel.get_status_count(
                employee_id)
            total_applicants = ApplicantManagementModel.get_total_applicants(
                employee_id)

            grouped_jobs = {}
            for applicant in applicants:
                job_id = applicant.get('Job_id')
                job_title = applicant.get('job_title') or 'Unknown Job'
                if job_id not in grouped_jobs:
                    grouped_jobs[job_id] = {
                        'job_id': job_id,
                        'job_title': job_title,
                        'total': 0,
                        'pending': 0,
                        'shortlisted': 0,
                        'rejected': 0,
                        'selected': 0,
                    }

                group = grouped_jobs[job_id]
                group['total'] += 1
                status = (applicant.get('Status') or 'pending').lower()
                if status == 'pending':
                    group['pending'] += 1
                elif status == 'shortlisted':
                    group['shortlisted'] += 1
                elif status == 'rejected':
                    group['rejected'] += 1
                elif status in ('accepted', 'hired'):
                    group['selected'] += 1

            grouped_jobs = sorted(
                grouped_jobs.values(),
                key=lambda item: item['job_title'].lower()
            )

            return render_template(
                "manage_applicants.html",
                user=user_data,
                applicants=applicants,
                job_groups=grouped_jobs,
                status_counts=status_counts,
                total_applicants=total_applicants
            )

        @self.blueprint.route("/employer/applicants/<int:job_id>", methods=["GET"])
        def list_job_applicants(job_id):
            if "user_id" not in session or session.get("role") != "employer":
                flash("Please log in as an employer.", "error")
                return redirect(url_for("login.index"))

            applicants = ApplicantManagementModel.get_applications_for_job(
                job_id)
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

            applicant = ApplicantManagementModel.get_application_details(
                application_id)
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

            status = request.json.get("status", "").strip().lower()
            valid_statuses = [
                "pending",
                "shortlisted",
                "accepted",
                "rejected",
                "under_review",
                "hired"
            ]

            if status not in valid_statuses:
                return jsonify({"status": "error", "message": "Invalid status."}), 400

            applicant = ApplicantManagementModel.get_application_details(
                application_id)
            if not applicant:
                return jsonify({"status": "error", "message": "Application not found."}), 404

            if status in ("accepted", "hired"):
                status = "hired"
                job_id = applicant.get("Job_id")
                if not job_id:
                    return jsonify({"status": "error", "message": "Job information missing."}), 400

                all_applications = ApplicantManagementModel.get_applications_for_job(
                    job_id)
                already_hired = any(
                    (app.get("Status") or "").lower() in ("hired", "accepted")
                    and app.get("Application_id") != application_id
                    for app in all_applications
                )
                if already_hired:
                    return jsonify({
                        "status": "error",
                        "message": "This job already has a hired applicant."
                    }), 400

                if ApplicantManagementModel.update_application_status(application_id, "hired"):
                    JobPostingModel.update_job_status(job_id, "closed")

                    job_record = JobPostingModel.get_job_by_id(job_id)
                    company_name = job_record.get(
                        "Company_name") if job_record else "the company"
                    job_title = applicant.get("job_title") or "this position"

                    seeker_user_id = applicant.get("job_seeker_user_id")
                    if seeker_user_id:
                        NotificationController.create_notification(
                            seeker_user_id,
                            "Congratulations! You have been selected",
                            f"You have been selected for the position of {job_title} at {company_name}."
                        )

                    for other in all_applications:
                        other_id = other.get("Application_id")
                        if other_id == application_id:
                            continue
                        if (other.get("Status") or "").lower() not in ("hired", "accepted"):
                            ApplicantManagementModel.update_application_status(
                                other_id, "rejected")
                            other_user_id = other.get("job_seeker_user_id")
                            if other_user_id:
                                NotificationController.create_notification(
                                    other_user_id,
                                    "Application Update",
                                    f"Your application for {job_title} was not selected at this time."
                                )

                    return jsonify({
                        "status": "success",
                        "message": "Application marked as hired and the vacancy has been closed."
                    }), 200
                return jsonify({"status": "error", "message": "Failed to update application status."}), 500

            if status == "rejected":
                if ApplicantManagementModel.update_application_status(application_id, "rejected"):
                    job_title = applicant.get("job_title") or "this position"
                    seeker_user_id = applicant.get("job_seeker_user_id")
                    if seeker_user_id:
                        NotificationController.create_notification(
                            seeker_user_id,
                            "Application Update",
                            f"Your application for {job_title} was not selected at this time."
                        )
                    return jsonify({
                        "status": "success",
                        "message": "Application marked as rejected."
                    }), 200
                return jsonify({"status": "error", "message": "Failed to update application status."}), 500

            if ApplicantManagementModel.update_application_status(application_id, status):
                return jsonify({
                    "status": "success",
                    "message": f"Application status updated to {status}."
                }), 200
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
                    cur.execute(
                        "SELECT `Seekers_id` FROM `Job_Seekers` WHERE `User_id`=%s", (user_id,))
                    seeker = cur.fetchone()
                    if not seeker:
                        flash("Job seeker profile not found.", "error")
                        return redirect(url_for("job_seeker.dashboard"))

                    seekers_id = seeker['Seekers_id']

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
