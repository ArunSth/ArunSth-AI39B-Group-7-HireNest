from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.modals.job_posting_model import JobPostingModel
from app.modals.employer_profile import EmployerProfileModel
from app.modals.user import UserModel
from app.modals.applicant_management_model import ApplicantManagementModel
from app.modals.job_seeker_profile import JobSeekerProfileModel

class JobPostingRoutes:
    def __init__(self):
        self.blueprint = Blueprint("job_posting", __name__)

    def job_posting(self):
        @self.blueprint.route("/jobs", methods=["GET"])
        def browse_jobs():
            keyword = request.args.get("keyword", "").strip()
            location = request.args.get("location", "").strip()
            job_type = request.args.get("job_type", "All Types").strip()
            jobs = JobPostingModel.search_jobs(keyword, location, job_type)
            saved_job_ids = set()
            if session.get("user_id") and session.get("role") == "job_seeker":
                seeker_profile = JobSeekerProfileModel.get_profile_by_user_id(session["user_id"])
                if seeker_profile:
                    saved_job_ids = JobPostingModel.get_saved_job_ids(seeker_profile["Seekers_id"])
            return render_template(
                "job_search.html",
                jobs=jobs,
                keyword=keyword,
                location=location,
                job_type=job_type,
                saved_job_ids=saved_job_ids,
                saved_only=False,
            )

        @self.blueprint.route("/saved-jobs", methods=["GET"])
        def saved_jobs():
            if "user_id" not in session or session.get("role") != "job_seeker":
                flash("Please log in as a job seeker to view saved jobs.", "error")
                return redirect(url_for("login.index"))

            seeker_profile = JobSeekerProfileModel.get_profile_by_user_id(session["user_id"])
            if not seeker_profile:
                flash("Complete your job seeker profile first.", "error")
                return redirect(url_for("job_seeker.profile"))

            jobs = JobPostingModel.get_saved_jobs(seeker_profile["Seekers_id"])
            saved_job_ids = {job["Job_id"] for job in jobs}
            return render_template(
                "job_search.html",
                jobs=jobs,
                keyword="",
                location="",
                job_type="All Types",
                saved_job_ids=saved_job_ids,
                saved_only=True,
            )

        @self.blueprint.route("/jobs/<int:job_id>", methods=["GET"])
        def seeker_job_detail(job_id):
            if "user_id" not in session or session.get("role") != "job_seeker":
                flash("Please log in as a job seeker to view job details.", "error")
                return redirect(url_for("login.index"))

            job = JobPostingModel.get_job_by_id(job_id)
            if not job or job.get("Status") != "active":
                flash("Job not found.", "error")
                return redirect(url_for("job_posting.browse_jobs"))

            seeker_profile = JobSeekerProfileModel.get_profile_by_user_id(session["user_id"])
            application = None
            is_saved = False
            if seeker_profile:
                application = ApplicantManagementModel.get_application_for_job(seeker_profile["Seekers_id"], job_id)
                is_saved = job_id in JobPostingModel.get_saved_job_ids(seeker_profile["Seekers_id"])

            return render_template(
                "seeker_job_detail.html",
                job=job,
                seeker_profile=seeker_profile,
                application=application,
                is_saved=is_saved,
            )

        @self.blueprint.route("/jobs/<int:job_id>/apply", methods=["POST"])
        def apply_job(job_id):
            if "user_id" not in session or session.get("role") != "job_seeker":
                flash("Please log in as a job seeker to apply.", "error")
                return redirect(url_for("login.index"))

            job = JobPostingModel.get_job_by_id(job_id)
            if not job or job.get("Status") != "active":
                flash("Job not found.", "error")
                return redirect(url_for("job_posting.browse_jobs"))

            seeker_profile = JobSeekerProfileModel.get_profile_by_user_id(session["user_id"])
            if not seeker_profile:
                flash("Complete your job seeker profile before applying.", "error")
                return redirect(url_for("job_seeker.profile"))

            existing_application = ApplicantManagementModel.get_application_for_job(seeker_profile["Seekers_id"], job_id)
            if existing_application:
                flash("You have already applied for this job.", "error")
                return redirect(url_for("job_posting.seeker_job_detail", job_id=job_id))

            cover_letter = request.form.get("cover_letter", "").strip()
            application_id = ApplicantManagementModel.create_application(
                seeker_profile["Seekers_id"],
                job_id,
                seeker_profile.get("Resume"),
                cover_letter,
            )
            if application_id:
                flash("Application submitted successfully.", "success")
                return redirect(url_for("applicant.seeker_applications"))

            flash("Failed to submit application. Please try again.", "error")
            return redirect(url_for("job_posting.seeker_job_detail", job_id=job_id))

        @self.blueprint.route("/jobs/<int:job_id>/save", methods=["POST"])
        def save_job(job_id):
            if "user_id" not in session or session.get("role") != "job_seeker":
                flash("Please log in as a job seeker to save jobs.", "error")
                return redirect(url_for("login.index"))

            seeker_profile = JobSeekerProfileModel.get_profile_by_user_id(session["user_id"])
            if not seeker_profile:
                flash("Complete your job seeker profile first.", "error")
                return redirect(url_for("job_seeker.profile"))

            action = request.form.get("action", "save")
            if action == "remove":
                JobPostingModel.unsave_job(seeker_profile["Seekers_id"], job_id)
                flash("Job removed from saved jobs.", "success")
            else:
                JobPostingModel.save_job(seeker_profile["Seekers_id"], job_id)
                flash("Job saved.", "success")

            return redirect(request.referrer or url_for("job_posting.browse_jobs"))

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
                    cur.execute("SELECT `Employee_id` FROM `Employee` WHERE `User_id`=%s", (user_id,))
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
                job_app_counts[job["Job_id"]] = JobPostingModel.get_application_count(job["Job_id"])
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
                        cur.execute("SELECT `Employee_id` FROM `Employee` WHERE `User_id`=%s", (user_id,))
                        employee = cur.fetchone()
                        if not employee:
                            flash("Employer profile not found.", "error")
                            return redirect(url_for("employer.profile"))
                        
                        employee_id = employee['Employee_id']
                finally:
                    conn.close()

                title = request.form.get("title", "").strip()
                description = request.form.get("description", "").strip()
                requirement = request.form.get("requirement", "").strip()
                salary = request.form.get("salary", "").strip()
                location = request.form.get("location", "").strip()
                job_type = request.form.get("job_type", "Full-time").strip()
                experience_level = request.form.get("experience_level", "Entry-level").strip()

                if not all([title, description, requirement, location]):
                    flash("All fields are required.", "error")
                    return redirect(url_for("job_posting.create_job"))

                try:
                    salary = float(salary) if salary else 0
                except ValueError:
                    flash("Salary must be a valid number.", "error")
                    return redirect(url_for("job_posting.create_job"))

                job_id = JobPostingModel.create_job(
                    employee_id, title, description, requirement, salary, location, job_type, experience_level
                )

                if job_id:
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
                experience_level = request.form.get("experience_level", "Entry-level").strip()

                if not all([title, description, requirement, location]):
                    flash("All fields are required.", "error")
                    return redirect(url_for("job_posting.edit_job", job_id=job_id))

                try:
                    salary = float(salary) if salary else 0
                except ValueError:
                    flash("Salary must be a valid number.", "error")
                    return redirect(url_for("job_posting.edit_job", job_id=job_id))

                if JobPostingModel.update_job(job_id, title, description, requirement, salary, location, job_type, experience_level):
                    flash("Job updated successfully!", "success")
                    return redirect(url_for("job_posting.view_job", job_id=job_id))
                else:
                    flash("Failed to update job. Please try again.", "error")
                    return redirect(url_for("job_posting.edit_job", job_id=job_id))

            user_data = UserModel.get_by_id(session["user_id"])
            return render_template("edit_job.html", user=user_data, job=job)

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
            if status not in ["active", "closed", "archived"]:
                return jsonify({"status": "error", "message": "Invalid status."}), 400

            if JobPostingModel.update_job_status(job_id, status):
                return jsonify({"status": "success", "message": f"Job status updated to {status}."}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to update job status."}), 500

        return self.blueprint
