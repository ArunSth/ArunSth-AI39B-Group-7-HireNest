from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.controllers.job_alert_controller import JobAlertController
from app.controllers.notification_controller import NotificationController
from app.modals.job_posting_model import JobPostingModel
from app.modals.employer_profile import EmployerProfileModel
from app.modals.user import UserModel
from app.modals.applicant_management_model import ApplicantManagementModel
from app.modals.job_seeker_profile import JobSeekerProfileModel


class JobPostingRoutes:
    def __init__(self):
        self.blueprint = Blueprint("job_posting", __name__)

    def job_posting(self):
        @self.blueprint.route("/employer/jobs", methods=["GET"])
        def list_jobs():
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

            jobs = JobPostingModel.get_jobs_by_employer(employee_id)
            job_app_counts = {}
            for job in jobs:
                job_app_counts[job["Job_id"]] = JobPostingModel.get_application_count(
                    job["Job_id"])
            user_data = UserModel.get_by_id(user_id)

            return render_template("manage_jobs.html", user=user_data, jobs=jobs, job_app_counts=job_app_counts)

        @self.blueprint.route("/employer/jobs/create", methods=["GET", "POST"])
        def create_job():
            if "user_id" not in session or session.get("role") != "employer":
                flash("Please log in as an employer.", "error")
                return redirect(url_for("login.index"))

            if request.method == "POST":
                user_id = session["user_id"]

                # Get employer profile
                from app.database import get_connection
                conn = get_connection()
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT `Employee_id`, `Industry` FROM `Employee` WHERE `User_id`=%s",
                            (user_id,),
                        )
                        employee = cur.fetchone()
                        if not employee:
                            flash("Employer profile not found.", "error")
                            return redirect(url_for("employer.profile"))

                        employee_id = employee['Employee_id']
                        employer_industry = employee.get('Industry')
                finally:
                    conn.close()

                title = request.form.get("title", "").strip()
                description = request.form.get("description", "").strip()
                requirement = request.form.get("requirement", "").strip()
                salary = request.form.get("salary", "").strip()
                location = request.form.get("location", "").strip()
                job_type = request.form.get("job_type", "Full-time").strip()
                experience_level = request.form.get(
                    "experience_level", "Entry-level").strip()
                vacancies_raw = request.form.get("vacancies", "1").strip()

                if not all([title, description, requirement, location]):
                    flash("All fields are required.", "error")
                    return redirect(url_for("job_posting.create_job"))

                try:
                    salary = float(salary) if salary else 0
                except ValueError:
                    flash("Salary must be a valid number.", "error")
                    return redirect(url_for("job_posting.create_job"))

                from flask import current_app
                admin_settings = current_app.config.get('ADMIN_SETTINGS', {})
                initial_status = "Approved" if admin_settings.get('autoApproveJobs') else "Pending"
                if not admin_settings.get('jobModeration', True):
                    initial_status = "Approved"

                if admin_settings.get('employerVerification'):
                    if not employee.get('Company_name') or not employee.get('Industry') or not employee.get('Description') or not employee.get('Website'):
                        flash(
                            "Employer verification is required before posting jobs. Please complete your profile.",
                            "error"
                        )
                        return redirect(url_for("employer.profile"))

                try:
                    vacancies = int(vacancies_raw) if vacancies_raw else 1
                    if vacancies < 1:
                        raise ValueError
                except ValueError:
                    flash(
                        "Vacancies must be a valid whole number greater than 0.", "error")
                    return redirect(url_for("job_posting.create_job"))

                job_id = JobPostingModel.create_job(
                    employee_id, title, description, requirement, salary, location,
                    job_type, experience_level, vacancies, status=initial_status
                )

                if job_id:
                    matching_users = JobAlertController.match_job_seekers_for_job(
                        title,
                        location,
                        job_type,
                        employer_industry,
                        description,
                        requirement,
                    )
                    for user_id in matching_users:
                        NotificationController.create_notification(
                            user_id,
                            'New job matches your alert',
                            f"A new job posting for {title} matches your saved alert. Check it out!",
                            'job_alert',
                            reference_id=job_id,
                        )

                    flash("Job posted successfully!", "success")
                    return redirect(url_for("job_posting.list_jobs"))
                else:
                    flash("Failed to post job. Please try again.", "error")
                    return redirect(url_for("job_posting.create_job"))

            user_data = UserModel.get_by_id(session["user_id"])
            return render_template("post_job.html", user=user_data)

        @self.blueprint.route("/employer/jobs/<int:job_id>", methods=["GET"])
        def view_job(job_id):
            if "user_id" not in session or session.get("role") != "employer":
                flash("Please log in as an employer.", "error")
                return redirect(url_for("login.index"))

            job = JobPostingModel.get_job_by_id(job_id)
            if not job:
                flash("Job not found.", "error")
                return redirect(url_for("job_posting.list_jobs"))

            user_data = UserModel.get_by_id(session["user_id"])
            app_count = JobPostingModel.get_application_count(job_id)

            return render_template("job_detail.html", user=user_data, job=job, app_count=app_count)

        @self.blueprint.route("/employer/jobs/<int:job_id>/edit", methods=["GET", "POST"])
        def edit_job(job_id):
            if "user_id" not in session or session.get("role") != "employer":
                flash("Please log in as an employer.", "error")
                return redirect(url_for("login.index"))

            job = JobPostingModel.get_job_by_id(job_id)
            if not job:
                flash("Job not found.", "error")
                return redirect(url_for("job_posting.list_jobs"))

            if request.method == "POST":
                title = request.form.get("title", "").strip()
                description = request.form.get("description", "").strip()
                requirement = request.form.get("requirement", "").strip()
                salary = request.form.get("salary", "").strip()
                location = request.form.get("location", "").strip()
                job_type = request.form.get("job_type", "Full-time").strip()
                experience_level = request.form.get(
                    "experience_level", "Entry-level").strip()
                vacancies_raw = request.form.get("vacancies", "1").strip()

                if not all([title, description, requirement, location]):
                    flash("All fields are required.", "error")
                    return redirect(url_for("job_posting.edit_job", job_id=job_id))

                try:
                    salary = float(salary) if salary else 0
                except ValueError:
                    flash("Salary must be a valid number.", "error")
                    return redirect(url_for("job_posting.edit_job", job_id=job_id))

                try:
                    vacancies = int(vacancies_raw) if vacancies_raw else 1
                    if vacancies < 1:
                        raise ValueError
                except ValueError:
                    flash(
                        "Vacancies must be a valid whole number greater than 0.", "error")
                    return redirect(url_for("job_posting.edit_job", job_id=job_id))

                if JobPostingModel.update_job(
                    job_id, title, description, requirement, salary, location,
                    job_type, experience_level, vacancies
                ):
                    flash("Job updated successfully!", "success")
                    return redirect(url_for("job_posting.view_job", job_id=job_id))
                else:
                    flash("Failed to update job. Please try again.", "error")
                    return redirect(url_for("job_posting.edit_job", job_id=job_id))

            user_data = UserModel.get_by_id(session["user_id"])
            total_vacancies = int(job.get("Vacancies", 1) or 1)
            filled_positions = int(job.get("Filled_vacancies", 0) or 0)
            remaining_positions = max(total_vacancies - filled_positions, 0)
            return render_template(
                "edit_job.html",
                user=user_data,
                job=job,
                remaining_positions=remaining_positions
            )

        @self.blueprint.route("/employer/jobs/<int:job_id>/delete", methods=["POST"])
        def delete_job(job_id):
            if "user_id" not in session or session.get("role") != "employer":
                return jsonify({"status": "error", "message": "Unauthorized"}), 401

            if JobPostingModel.delete_job(job_id):
                return jsonify({"status": "success", "message": "Job deleted successfully."}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to delete job."}), 500

        @self.blueprint.route("/employer/jobs/<int:job_id>/status", methods=["POST"])
        def update_job_status(job_id):
            if "user_id" not in session or session.get("role") != "employer":
                return jsonify({"status": "error", "message": "Unauthorized"}), 401

            status = request.json.get("status", "").strip()
            if status not in ["Pending", "Approved", "Rejected", "Closed"]:
                return jsonify({"status": "error", "message": "Invalid status."}), 400

            if JobPostingModel.update_job_status(job_id, status):
                return jsonify({"status": "success", "message": f"Job status updated to {status}."}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to update job status."}), 500

        return self.blueprint
