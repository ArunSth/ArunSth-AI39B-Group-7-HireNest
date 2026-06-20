"""
Skill Assessment Routes
=======================
Routes for the Skills Assessment feature (Feature 26).

URL Map
-------
GET   /seeker/assessments                       -> list available + my attempts
GET   /seeker/assessments/<assessment_id>       -> assessment intro / start page
POST  /seeker/assessments/<assessment_id>/start -> create attempt -> redirect to take page
GET   /seeker/assessments/take/<attempt_id>     -> take the test
POST  /seeker/assessments/take/<attempt_id>     -> submit answers
GET   /seeker/assessments/result/<attempt_id>   -> view single result
"""

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, jsonify
)

from app.modals.skill_assessment_model import (
    SkillAssessmentModel, COOLDOWN_DAYS, PASS_PERCENTAGE
)
from app.modals.user import UserModel
from app.modals.job_seeker_profile import JobSeekerProfileModel
from app.modals.notification import NotificationModel


class SkillAssessmentRoutes:
    def __init__(self):
        self.blueprint = Blueprint("skill_assessment", __name__)

    # ------------------------------------------------------------------
    #  Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _require_seeker():
        """
        Returns (user_id, seekers_id) when authorized as a job_seeker
        with an existing seeker profile, otherwise returns (None, None).
        Caller is responsible for redirecting.
        """
        if "user_id" not in session or session.get("role") != "job_seeker":
            return None, None
        user_id = session["user_id"]
        JobSeekerProfileModel.ensure_profile_exists(user_id)
        profile = JobSeekerProfileModel.get_profile_by_user_id(user_id)
        if not profile:
            return user_id, None
        return user_id, profile["Seekers_id"]

    # ------------------------------------------------------------------
    #  Route registration
    # ------------------------------------------------------------------
    def register_routes(self):

        # ----- 1. List available assessments + my attempts -------------
        @self.blueprint.route("/seeker/assessments", methods=["GET"])
        def index():
            user_id, seekers_id = self._require_seeker()
            if not user_id:
                flash("Please log in as a job seeker.", "error")
                return redirect(url_for("login.index"))
            if not seekers_id:
                flash("Please complete your job seeker profile first.", "error")
                return redirect(url_for("job_seeker.profile"))

            assessments = SkillAssessmentModel.get_all_assessments()
            attempts = SkillAssessmentModel.get_attempts_for_seeker(seekers_id)

            # latest attempt per assessment_id for the badge column on listing
            latest_by_assessment = {}
            for a in attempts:
                aid = a["Assessment_id"]
                if aid not in latest_by_assessment:
                    latest_by_assessment[aid] = a

            user_data = UserModel.get_by_id(user_id)
            return render_template(
                "skill_assessments.html",
                user=user_data,
                assessments=assessments,
                attempts=attempts,
                latest_by_assessment=latest_by_assessment,
                pass_percentage=PASS_PERCENTAGE,
                cooldown_days=COOLDOWN_DAYS,
            )

        # ----- 2. Assessment intro page --------------------------------
        @self.blueprint.route("/seeker/assessments/<int:assessment_id>", methods=["GET"])
        def detail(assessment_id):
            user_id, seekers_id = self._require_seeker()
            if not user_id:
                flash("Please log in as a job seeker.", "error")
                return redirect(url_for("login.index"))
            if not seekers_id:
                flash("Please complete your job seeker profile first.", "error")
                return redirect(url_for("job_seeker.profile"))

            assessment = SkillAssessmentModel.get_assessment_by_id(assessment_id)
            if not assessment:
                flash("Assessment not found.", "error")
                return redirect(url_for("skill_assessment.index"))

            questions = SkillAssessmentModel.get_questions_for_assessment(
                assessment_id, include_correct=False
            )
            allowed, next_available = SkillAssessmentModel.can_retake(
                seekers_id, assessment_id
            )
            last = SkillAssessmentModel.get_latest_attempt(seekers_id, assessment_id)

            return render_template(
                "skill_assessment_detail.html",
                user=UserModel.get_by_id(user_id),
                assessment=assessment,
                question_count=len(questions),
                allowed=allowed,
                next_available=next_available,
                last_attempt=last,
                pass_percentage=PASS_PERCENTAGE,
                cooldown_days=COOLDOWN_DAYS,
            )

        # ----- 3. Start an attempt -------------------------------------
        @self.blueprint.route("/seeker/assessments/<int:assessment_id>/start", methods=["POST"])
        def start(assessment_id):
            user_id, seekers_id = self._require_seeker()
            if not user_id:
                flash("Please log in as a job seeker.", "error")
                return redirect(url_for("login.index"))
            if not seekers_id:
                flash("Please complete your job seeker profile first.", "error")
                return redirect(url_for("job_seeker.profile"))

            assessment = SkillAssessmentModel.get_assessment_by_id(assessment_id)
            if not assessment:
                flash("Assessment not found.", "error")
                return redirect(url_for("skill_assessment.index"))

            allowed, next_available = SkillAssessmentModel.can_retake(
                seekers_id, assessment_id
            )
            if not allowed:
                flash(
                    f"You can retake this assessment after "
                    f"{next_available.strftime('%d %b %Y, %H:%M')}.",
                    "error",
                )
                return redirect(url_for("skill_assessment.detail",
                                        assessment_id=assessment_id))

            attempt_id = SkillAssessmentModel.start_attempt(seekers_id, assessment_id)
            if not attempt_id:
                flash("Could not start the assessment. Please try again.", "error")
                return redirect(url_for("skill_assessment.detail",
                                        assessment_id=assessment_id))
            return redirect(url_for("skill_assessment.take", attempt_id=attempt_id))

        # ----- 4. Take / Submit ----------------------------------------
        @self.blueprint.route("/seeker/assessments/take/<int:attempt_id>",
                              methods=["GET", "POST"])
        def take(attempt_id):
            user_id, seekers_id = self._require_seeker()
            if not user_id:
                flash("Please log in as a job seeker.", "error")
                return redirect(url_for("login.index"))
            if not seekers_id:
                flash("Please complete your job seeker profile first.", "error")
                return redirect(url_for("job_seeker.profile"))

            # Verify the attempt belongs to this seeker
            from app.database import get_connection
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT * FROM `Seeker_Assessment_Attempts` WHERE `Attempt_id`=%s",
                        (attempt_id,),
                    )
                    attempt = cur.fetchone()
            finally:
                conn.close()

            if not attempt or attempt["Seekers_id"] != seekers_id:
                flash("Invalid assessment attempt.", "error")
                return redirect(url_for("skill_assessment.index"))

            if attempt["Status"] != "in_progress":
                flash("This attempt has already been submitted.", "info")
                return redirect(url_for("skill_assessment.result",
                                        attempt_id=attempt_id))

            assessment = SkillAssessmentModel.get_assessment_by_id(
                attempt["Assessment_id"]
            )
            questions = SkillAssessmentModel.get_questions_for_assessment(
                attempt["Assessment_id"], include_correct=False
            )

            # ----- POST = submit answers -----
            if request.method == "POST":
                answers = {}
                for q in questions:
                    qid = str(q["Question_id"])
                    answers[qid] = request.form.get(f"q_{qid}", "").strip()

                result = SkillAssessmentModel.submit_attempt(attempt_id, answers)
                if not result:
                    flash("There was a problem grading your test. Please contact support.",
                          "error")
                    return redirect(url_for("skill_assessment.index"))

                # Notify the user (in-app notification)
                try:
                    NotificationModel.create_notification(
                        user_id=user_id,
                        title="Assessment Result",
                        message=(f"You scored {result['score']}% on "
                                 f"'{assessment['Title']}'. "
                                 f"{'You earned a verified badge!' if result['passed'] else 'Keep practising and try again after the cooldown.'}"),
                        notification_type="assessment",
                        reference_id=attempt_id,
                    )
                except Exception as e:
                    # never let notification failure break the flow
                    print(f"[skill_assessment.take] notification failed: {e}")

                if result["passed"]:
                    flash(f"Congratulations! You passed with {result['score']}%.",
                          "success")
                else:
                    flash(f"You scored {result['score']}%. "
                          f"Required: {PASS_PERCENTAGE}%.",
                          "info")
                return redirect(url_for("skill_assessment.result",
                                        attempt_id=attempt_id))

            # ----- GET = render the test -----
            return render_template(
                "skill_assessment_take.html",
                user=UserModel.get_by_id(user_id),
                assessment=assessment,
                attempt=attempt,
                questions=questions,
            )

        # ----- 5. Result page ------------------------------------------
        @self.blueprint.route("/seeker/assessments/result/<int:attempt_id>",
                              methods=["GET"])
        def result(attempt_id):
            user_id, seekers_id = self._require_seeker()
            if not user_id:
                flash("Please log in as a job seeker.", "error")
                return redirect(url_for("login.index"))
            if not seekers_id:
                flash("Please complete your job seeker profile first.", "error")
                return redirect(url_for("job_seeker.profile"))

            from app.database import get_connection
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT a.*, s.`Title`, s.`Total_marks`, s.`Duration_minutes`
                        FROM   `Seeker_Assessment_Attempts` a
                        JOIN   `Skills_Assessments` s
                                 ON a.`Assessment_id` = s.`Assessment_id`
                        WHERE  a.`Attempt_id` = %s
                        """,
                        (attempt_id,),
                    )
                    attempt = cur.fetchone()
            finally:
                conn.close()

            if not attempt or attempt["Seekers_id"] != seekers_id:
                flash("Result not found.", "error")
                return redirect(url_for("skill_assessment.index"))

            allowed, next_available = SkillAssessmentModel.can_retake(
                seekers_id, attempt["Assessment_id"]
            )

            return render_template(
                "skill_assessment_result.html",
                user=UserModel.get_by_id(user_id),
                attempt=attempt,
                allowed=allowed,
                next_available=next_available,
                pass_percentage=PASS_PERCENTAGE,
                cooldown_days=COOLDOWN_DAYS,
            )

        return self.blueprint
