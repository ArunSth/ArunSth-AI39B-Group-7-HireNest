
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app.modals.employer_profile import EmployerProfileModel
from app.modals.user import UserModel
from app.modals.job_posting_model import JobPostingModel
from app.modals.applicant_management_model import ApplicantManagementModel
from app.modals.interview_scheduling_model import InterviewSchedulingModel
import os


class EmployerRoutes:
    def __init__(self):
        self.blueprint = Blueprint("employer", __name__)

    def register_routes(self):
        """Register all employer routes"""
        self.employer_profile()
        return self.blueprint

    def employer_profile(self):
        @self.blueprint.route("/employer/dashboard", methods=["GET"])
        def dashboard():
            if "user_id" not in session or session.get("role") != "employer":
                flash("Please log in as an employer to view your dashboard.", "error")
                return redirect(url_for("login.index"))

            user_id = session["user_id"]
            user_data = UserModel.get_by_id(user_id)

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

            profile_data = EmployerProfileModel.get_profile_by_user_id(user_id)
            completion_percentage = EmployerProfileModel.calculate_profile_completion(
                user_id)
            jobs = JobPostingModel.get_jobs_by_employer(employee_id)
            applicants = ApplicantManagementModel.get_applications_for_employer(
                employee_id)
            interviews = InterviewSchedulingModel.get_interviews_for_employer(
                employee_id)

            # Calculate stats
            total_applicants = ApplicantManagementModel.get_total_applicants(
                employee_id)
            job_app_counts = {}
            for job in jobs:
                job_app_counts[job['Job_id']] = JobPostingModel.get_application_count(
                    job['Job_id'])

            return render_template(
                "employer_dashboard.html",
                user=user_data,
                profile=profile_data,
                jobs=jobs,
                recent_applications=applicants[:5] if applicants else [],
                interviews=interviews,
                total_applicants=total_applicants,
                completion_percentage=completion_percentage,
                job_app_counts=job_app_counts
            )

        @self.blueprint.route("/employer/profile", methods=["GET", "POST"])
        def profile():
            if "user_id" not in session or session.get("role") != "employer":
                flash("Please log in as an employer to view your profile.", "error")
                return redirect(url_for("login.index"))

            user_id = session["user_id"]
            # Assuming a get_by_id method exists in UserModel
            user_data = UserModel.get_by_id(user_id)
            profile_data = EmployerProfileModel.get_profile_by_user_id(user_id)
            completion_percentage = EmployerProfileModel.calculate_profile_completion(
                user_id)

            if request.method == "POST":
                company_name = request.form.get("company_name", "").strip()
                industry = request.form.get("industry", "").strip()
                description = request.form.get("description", "").strip()
                website = request.form.get("website", "").strip()
                action = request.form.get("action")

                if EmployerProfileModel.create_or_update_profile(user_id, company_name, industry, description, website):
                    # Recalculate and update completion percentage
                    new_completion_percentage = EmployerProfileModel.calculate_profile_completion(
                        user_id)
                    EmployerProfileModel.update_profile_completion(
                        user_id, new_completion_percentage)

                    flash("Company profile updated successfully!", "success")
                    if action == "save_and_dashboard":
                        return redirect(url_for("employer.dashboard"))
                    return redirect(url_for("employer.profile"))
                else:
                    flash(
                        "Failed to update company profile. Please try again.", "error")

            return render_template("employer_profile.html", user=user_data, profile=profile_data, completion_percentage=completion_percentage)

        @self.blueprint.route("/employer/profile/logo", methods=["POST"])
        def upload_logo():
            if "user_id" not in session or session.get("role") != "employer":
                return jsonify({"status": "error", "message": "Unauthorized"}), 401

            user_id = session["user_id"]

            if "logo" not in request.files:
                return jsonify({"status": "error", "message": "No logo file provided"}), 400

            logo_file = request.files["logo"]

            if logo_file.filename == "":
                return jsonify({"status": "error", "message": "No selected file"}), 400

            if logo_file and self._allowed_logo_file(logo_file.filename):
                # Create a directory for logos if it doesn"t exist
                upload_folder = os.path.join(os.getcwd(), "uploads", "logos")
                os.makedirs(upload_folder, exist_ok=True)

                filename = f"logo_{user_id}.{logo_file.filename.rsplit('.', 1)[1].lower()}"
                filepath = os.path.join(upload_folder, filename)
                logo_file.save(filepath)

                if EmployerProfileModel.update_logo(user_id, filename):
                    # Recalculate and update completion percentage
                    new_completion_percentage = EmployerProfileModel.calculate_profile_completion(
                        user_id)
                    EmployerProfileModel.update_profile_completion(
                        user_id, new_completion_percentage)

                    return jsonify({"status": "success", "message": "Company logo uploaded successfully!", "filename": filename}), 200
                else:
                    return jsonify({"status": "error", "message": "Failed to save logo path to database"}), 500
            else:
                return jsonify({"status": "error", "message": "Invalid file type or size. Accepted: JPG, PNG (max 5MB)"}), 400

        return self.blueprint

    def _allowed_logo_file(self, filename):
        if "." not in filename:
            return False

        if filename.rsplit(".", 1)[1].lower() not in ["jpg", "png", "jpeg"]:
            return False

        content_length = request.content_length
        if content_length is not None and content_length > 5 * 1024 * 1024:
            return False

        return True
