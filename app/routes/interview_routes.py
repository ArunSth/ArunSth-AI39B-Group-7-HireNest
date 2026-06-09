from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.modals.interview_scheduling_model import InterviewSchedulingModel
from app.modals.applicant_management_model import ApplicantManagementModel
from app.modals.user import UserModel

class InterviewRoutes:
    def __init__(self):
        self.blueprint = Blueprint("interview", __name__)

    def interview_scheduling(self):
        @self.blueprint.route("/employer/interviews", methods=["GET"])
        def list_interviews():
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

            interviews = InterviewSchedulingModel.get_interviews_for_employer(employee_id)
            user_data = UserModel.get_by_id(user_id)
            status_counts = InterviewSchedulingModel.get_interview_count_by_status(employee_id)
            
            return render_template(
                "interview_list.html", 
                user=user_data, 
                interviews=interviews,
                status_counts=status_counts
            )

        @self.blueprint.route("/employer/interview/schedule/<int:application_id>", methods=["GET", "POST"])
        def schedule_interview(application_id):
            if "user_id" not in session or session.get("role") != "employer":
                flash("Please log in as an employer.", "error")
                return redirect(url_for("login.index"))

            applicant = ApplicantManagementModel.get_application_details(application_id)
            if not applicant:
                flash("Application not found.", "error")
                return redirect(url_for("applicant.list_applicants"))

            if request.method == "POST":
                interview_date = request.form.get("interview_date", "").strip()
                interview_time = request.form.get("interview_time", "").strip()
                meeting_link = request.form.get("meeting_link", "").strip()
                mode = request.form.get("mode", "Google Meet").strip()

                if not all([interview_date, interview_time, meeting_link]):
                    flash("All fields are required.", "error")
                    return redirect(url_for("interview.schedule_interview", application_id=application_id))

                interview_id = InterviewSchedulingModel.schedule_interview(
                    application_id, interview_date, interview_time, meeting_link, mode, "scheduled"
                )

                if interview_id:
                    # Update application status to shortlisted
                    ApplicantManagementModel.update_application_status(application_id, "shortlisted")
                    
                    flash("Interview scheduled successfully!", "success")
                    return redirect(url_for("interview.list_interviews"))
                else:
                    flash("Failed to schedule interview. Please try again.", "error")
                    return redirect(url_for("interview.schedule_interview", application_id=application_id))

            user_data = UserModel.get_by_id(session["user_id"])
            return render_template("schedule_interview.html", user=user_data, applicant=applicant, application_id=application_id)

        @self.blueprint.route("/employer/interview/<int:interview_id>", methods=["GET"])
        def view_interview(interview_id):
            if "user_id" not in session or session.get("role") != "employer":
                flash("Please log in as an employer.", "error")
                return redirect(url_for("login.index"))

            interview = InterviewSchedulingModel.get_interview_details(interview_id)
            if not interview:
                flash("Interview not found.", "error")
                return redirect(url_for("interview.list_interviews"))

            user_data = UserModel.get_by_id(session["user_id"])
            return render_template("interview_detail.html", user=user_data, interview=interview)

        @self.blueprint.route("/employer/interview/<int:interview_id>/edit", methods=["GET", "POST"])
        def edit_interview(interview_id):
            if "user_id" not in session or session.get("role") != "employer":
                flash("Please log in as an employer.", "error")
                return redirect(url_for("login.index"))

            interview = InterviewSchedulingModel.get_interview_by_id(interview_id)
            if not interview:
                flash("Interview not found.", "error")
                return redirect(url_for("interview.list_interviews"))

            if request.method == "POST":
                interview_date = request.form.get("interview_date", "").strip()
                interview_time = request.form.get("interview_time", "").strip()
                meeting_link = request.form.get("meeting_link", "").strip()
                mode = request.form.get("mode", "Google Meet").strip()
                status = request.form.get("status", "scheduled").strip()

                if not all([interview_date, interview_time, meeting_link]):
                    flash("All fields are required.", "error")
                    return redirect(url_for("interview.edit_interview", interview_id=interview_id))

                if InterviewSchedulingModel.update_interview(interview_id, interview_date, interview_time, meeting_link, mode, status):
                    flash("Interview updated successfully!", "success")
                    return redirect(url_for("interview.view_interview", interview_id=interview_id))
                else:
                    flash("Failed to update interview. Please try again.", "error")
                    return redirect(url_for("interview.edit_interview", interview_id=interview_id))

            user_data = UserModel.get_by_id(session["user_id"])
            return render_template("edit_interview.html", user=user_data, interview=interview)

        @self.blueprint.route("/employer/interview/<int:interview_id>/status", methods=["POST"])
        def update_interview_status(interview_id):
            if "user_id" not in session or session.get("role") != "employer":
                return jsonify({"status": "error", "message": "Unauthorized"}), 401

            status = request.json.get("status", "").strip()
            valid_statuses = ["scheduled", "completed", "cancelled", "no-show", "rescheduled"]
            
            if status not in valid_statuses:
                return jsonify({"status": "error", "message": "Invalid status."}), 400

            if InterviewSchedulingModel.update_interview_status(interview_id, status):
                return jsonify({"status": "success", "message": f"Interview status updated to {status}."}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to update interview status."}), 500

        @self.blueprint.route("/seeker/interviews", methods=["GET"])
        def seeker_interviews():
            if "user_id" not in session or session.get("role") != "job_seeker":
                flash("Please log in as a job seeker.", "error")
                return redirect(url_for("login.index"))

            user_id = session["user_id"]
            
            # Get job seeker profile
            from app.database import get_connection
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT `Seekers_id` FROM `Job_Seekers` WHERE `User_id`=%s", (user_id,))
                    seeker = cur.fetchone()
                    if not seeker:
                        flash("Job seeker profile not found.", "error")
                        return redirect(url_for("job_seeker.profile"))
                    
                    seekers_id = seeker['Seekers_id']
            finally:
                conn.close()

            interviews = InterviewSchedulingModel.get_interviews_for_applicant(seekers_id)
            user_data = UserModel.get_by_id(user_id)

            return render_template(
                "seeker_interviews.html", 
                user=user_data, 
                interviews=interviews
            )

        @self.blueprint.route("/seeker/interview/<int:interview_id>", methods=["GET"])
        def seeker_view_interview(interview_id):
            if "user_id" not in session or session.get("role") != "job_seeker":
                flash("Please log in as a job seeker.", "error")
                return redirect(url_for("login.index"))

            interview = InterviewSchedulingModel.get_interview_details(interview_id)
            if not interview:
                flash("Interview not found.", "error")
                return redirect(url_for("interview.seeker_interviews"))

            user_data = UserModel.get_by_id(session["user_id"])
            return render_template("seeker_interview_detail.html", user=user_data, interview=interview)

        return self.blueprint
