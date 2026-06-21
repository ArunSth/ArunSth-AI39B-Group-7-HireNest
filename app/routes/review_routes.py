from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.controllers.review_controller import ReviewController
from app.modals.user import UserModel


class ReviewRoutes:
    def __init__(self):
        self.blueprint = Blueprint("reviews", __name__)

    def review_routes(self):
        @self.blueprint.route("/reviews", methods=["GET"])
        def reviews_index():
            if "user_id" not in session or session.get("role") != "job_seeker":
                flash("Please log in as a job seeker to view company reviews.", "error")
                return redirect(url_for("login.index"))

            user_data = UserModel.get_by_id(session["user_id"])
            seekers_id = self._get_seeker_id(session["user_id"])
            if seekers_id is None:
                flash("Job seeker profile not found.", "error")
                return redirect(url_for("job_seeker.dashboard"))

            from app.database import get_connection
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT DISTINCT e.Employee_id, e.Company_name
                        FROM `Applications` a
                        JOIN `Jobs` j ON a.Job_id = j.Job_id
                        JOIN `Employee` e ON j.Employee_id = e.Employee_id
                        WHERE a.Seekers_id = %s
                        ORDER BY e.Company_name
                        """,
                        (seekers_id,),
                    )
                    companies = cur.fetchall()
            finally:
                conn.close()

            return render_template(
                "reviews_index.html",
                user=user_data,
                companies=companies,
            )

        @self.blueprint.route("/seeker/company-review/<int:employee_id>", methods=["GET", "POST"])
        def company_review(employee_id):
            if "user_id" not in session or session.get("role") != "job_seeker":
                flash("Please log in as a job seeker to submit a review.", "error")
                return redirect(url_for("login.index"))

            user_data = UserModel.get_by_id(session["user_id"])
            seekers_id = self._get_seeker_id(session["user_id"])
            if seekers_id is None:
                flash("Job seeker profile not found.", "error")
                return redirect(url_for("job_seeker.dashboard"))

            review_summary = ReviewController.get_review_summary(employee_id)
            reviews = ReviewController.get_reviews_by_employee(employee_id)

            if request.method == "POST":
                review_text = request.form.get("review_text", "").strip()
                rating = request.form.get("rating", "").strip()

                if not review_text or not rating:
                    flash("Please provide both review text and rating.", "error")
                    return redirect(url_for("reviews.company_review", employee_id=employee_id))

                try:
                    rating_value = int(rating)
                except ValueError:
                    flash("Rating must be an integer between 1 and 5.", "error")
                    return redirect(url_for("reviews.company_review", employee_id=employee_id))

                if rating_value < 1 or rating_value > 5:
                    flash("Rating must be between 1 and 5.", "error")
                    return redirect(url_for("reviews.company_review", employee_id=employee_id))

                if ReviewController.create_review(seekers_id, employee_id, review_text, rating_value):
                    flash("Review submitted successfully.", "success")
                else:
                    flash("Failed to submit review. Please try again.", "error")

                return redirect(url_for("reviews.company_review", employee_id=employee_id))

            return render_template(
                "company_review.html",
                user=user_data,
                employee_id=employee_id,
                summary=review_summary,
                reviews=reviews,
                current_seekers_id=seekers_id,
                edit_review=None,
            )

        @self.blueprint.route("/seeker/company-review/<int:employee_id>/edit/<int:review_id>", methods=["GET", "POST"])
        def edit_review(employee_id, review_id):
            flash(
                "Editing reviews is not allowed. Please submit a new review if needed.", "error")
            return redirect(url_for("reviews.company_review", employee_id=employee_id))

        @self.blueprint.route("/seeker/company-review/<int:employee_id>/delete/<int:review_id>", methods=["POST"])
        def delete_review(employee_id, review_id):
            flash("Deleting reviews is not allowed.", "error")
            return redirect(url_for("reviews.company_review", employee_id=employee_id))

        return self.blueprint

    def _get_seeker_id(self, user_id):
        from app.database import get_connection
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT `Seekers_id` FROM `Job_Seekers` WHERE `User_id`=%s", (user_id,))
                seeker = cur.fetchone()
                return seeker["Seekers_id"] if seeker else None
        finally:
            conn.close()
