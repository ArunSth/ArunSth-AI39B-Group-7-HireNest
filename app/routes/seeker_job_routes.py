from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.modals.applicant_management_model import ApplicantManagementModel
from app.modals.job_posting_model import JobPostingModel
from app.modals.job_seeker_profile import JobSeekerProfileModel
from app.modals.saved_job_model import SavedJobModel
from app.modals.user import UserModel


class SeekerJobRoutes:
    def __init__(self):
        self.blueprint = Blueprint("seeker_jobs", __name__)

    def register_routes(self):
        @self.blueprint.route("/seeker/jobs", methods=["GET"])
        def index():
            if "user_id" not in session or session.get("role") != "job_seeker":
                flash("Please log in as a job seeker.", "error")
                return redirect(url_for("login.index"))

            user_id = session["user_id"]
            JobSeekerProfileModel.ensure_profile_exists(user_id)
            seeker_profile = JobSeekerProfileModel.get_profile_by_user_id(user_id)
            seekers_id = seeker_profile["Seekers_id"] if seeker_profile else None

            filters = {
                "keyword": request.args.get("keyword", "").strip(),
                "company": request.args.get("company", "").strip(),
                "location": request.args.get("location", "").strip(),
                "industry": request.args.get("industry", "").strip(),
                "job_type": request.args.get("job_type", "All Types").strip(),
                "experience_level": request.args.get("experience_level", "All Levels").strip(),
                "salary_min": request.args.get("salary_min", "").strip(),
                "salary_max": request.args.get("salary_max", "").strip(),
            }
            for salary_key in ("salary_min", "salary_max"):
                if filters[salary_key]:
                    try:
                        float(filters[salary_key])
                    except ValueError:
                        filters[salary_key] = ""
                        flash("Salary filters must be numeric.", "error")

            jobs = JobPostingModel.search_jobs_for_seekers(filters, seekers_id)
            user_data = UserModel.get_by_id(user_id)

            return render_template(
                "seeker_jobs.html",
                user=user_data,
                jobs=jobs,
                filters=filters,
                seeker_profile=seeker_profile,
            )

        @self.blueprint.route("/seeker/jobs/<int:job_id>", methods=["GET"])
        def detail(job_id):
            if "user_id" not in session or session.get("role") != "job_seeker":
                flash("Please log in as a job seeker.", "error")
                return redirect(url_for("login.index"))

            user_id = session["user_id"]
            JobSeekerProfileModel.ensure_profile_exists(user_id)
            seeker_profile = JobSeekerProfileModel.get_profile_by_user_id(user_id)
            seekers_id = seeker_profile["Seekers_id"] if seeker_profile else None
            job = JobPostingModel.get_job_detail_for_seeker(job_id, seekers_id)

            if not job or str(job.get("Status", "")).lower() != "active":
                flash("This job is no longer available.", "error")
                return redirect(url_for("seeker_jobs.index"))

            return render_template(
                "seeker_job_detail.html",
                user=UserModel.get_by_id(user_id),
                job=job,
                seeker_profile=seeker_profile,
            )

        @self.blueprint.route("/seeker/jobs/<int:job_id>/apply", methods=["POST"])
        def apply(job_id):
            if "user_id" not in session or session.get("role") != "job_seeker":
                flash("Please log in as a job seeker.", "error")
                return redirect(url_for("login.index"))

            user_id = session["user_id"]
            JobSeekerProfileModel.ensure_profile_exists(user_id)
            seeker_profile = JobSeekerProfileModel.get_profile_by_user_id(user_id)
            if not seeker_profile:
                flash("Please complete your job seeker profile before applying.", "error")
                return redirect(url_for("job_seeker.profile"))

            job = JobPostingModel.get_job_by_id(job_id)
            if not job or str(job.get("Status", "")).lower() != "active":
                flash("This job is no longer accepting applications.", "error")
                return redirect(url_for("seeker_jobs.index"))

            seekers_id = seeker_profile["Seekers_id"]
            if ApplicantManagementModel.has_applied(seekers_id, job_id):
                flash("You have already applied to this job.", "error")
                return redirect(url_for("seeker_jobs.detail", job_id=job_id))

            cover_letter = request.form.get("cover_letter", "").strip()
            resume = seeker_profile.get("Resume")
            created = ApplicantManagementModel.create_application(
                seekers_id, job_id, resume, cover_letter, "Pending"
            )

            if created:
                flash("Application submitted successfully.", "success")
            else:
                flash("Could not submit your application. Please try again.", "error")
            return redirect(url_for("seeker_jobs.detail", job_id=job_id))

        @self.blueprint.route("/seeker/jobs/<int:job_id>/save", methods=["POST"])
        def save(job_id):
            if "user_id" not in session or session.get("role") != "job_seeker":
                flash("Please log in as a job seeker.", "error")
                return redirect(url_for("login.index"))

            JobSeekerProfileModel.ensure_profile_exists(session["user_id"])
            seeker_profile = JobSeekerProfileModel.get_profile_by_user_id(session["user_id"])
            if not seeker_profile:
                flash("Please complete your job seeker profile before saving jobs.", "error")
                return redirect(url_for("job_seeker.profile"))

            job = JobPostingModel.get_job_by_id(job_id)
            if not job or str(job.get("Status", "")).lower() != "active":
                flash("This job is no longer available.", "error")
                return redirect(url_for("seeker_jobs.index"))

            if SavedJobModel.save_job(seeker_profile["Seekers_id"], job_id):
                flash("Job saved.", "success")
            else:
                flash("Could not save this job. Please try again.", "error")
            return redirect(request.referrer or url_for("seeker_jobs.detail", job_id=job_id))

        @self.blueprint.route("/seeker/jobs/<int:job_id>/unsave", methods=["POST"])
        def unsave(job_id):
            if "user_id" not in session or session.get("role") != "job_seeker":
                flash("Please log in as a job seeker.", "error")
                return redirect(url_for("login.index"))

            JobSeekerProfileModel.ensure_profile_exists(session["user_id"])
            seeker_profile = JobSeekerProfileModel.get_profile_by_user_id(session["user_id"])
            if not seeker_profile:
                flash("Please complete your job seeker profile first.", "error")
                return redirect(url_for("job_seeker.profile"))

            if SavedJobModel.unsave_job(seeker_profile["Seekers_id"], job_id):
                flash("Job removed from saved jobs.", "success")
            else:
                flash("Could not update saved jobs. Please try again.", "error")
            return redirect(request.referrer or url_for("seeker_jobs.saved_jobs"))

        @self.blueprint.route("/seeker/saved-jobs", methods=["GET"])
        def saved_jobs():
            if "user_id" not in session or session.get("role") != "job_seeker":
                flash("Please log in as a job seeker.", "error")
                return redirect(url_for("login.index"))

            user_id = session["user_id"]
            JobSeekerProfileModel.ensure_profile_exists(user_id)
            seeker_profile = JobSeekerProfileModel.get_profile_by_user_id(user_id)
            if not seeker_profile:
                flash("Please complete your job seeker profile first.", "error")
                return redirect(url_for("job_seeker.profile"))

            jobs = SavedJobModel.get_saved_jobs(seeker_profile["Seekers_id"])
            return render_template(
                "saved_jobs.html",
                user=UserModel.get_by_id(user_id),
                jobs=jobs,
                seeker_profile=seeker_profile,
            )

        return self.blueprint
