import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, Blueprint
from app.routes.review_routes import ReviewRoutes
from app.controllers.review_controller import ReviewController


def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"
    app.register_blueprint(ReviewRoutes().review_routes())

    login_bp = Blueprint("login", __name__)
    login_bp.route("/login", endpoint="index")(lambda: "login")
    app.register_blueprint(login_bp)

    job_seeker_bp = Blueprint("job_seeker", __name__)
    job_seeker_bp.route("/job-seeker/dashboard", endpoint="dashboard")(lambda: "dashboard")
    app.register_blueprint(job_seeker_bp)

    return app


def make_valid_session(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 5
        sess["role"] = "job_seeker"


def make_mock_connection(companies=None, seeker_id=None):
    mock_cursor = MagicMock()
    mock_cursor.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = companies if companies is not None else []
    mock_cursor.fetchone.return_value = {"Seekers_id": seeker_id} if seeker_id is not None else None
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn


class TestReviewRoutes(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()

    @patch("app.routes.review_routes.render_template")
    @patch("app.routes.review_routes.UserModel.get_by_id")
    @patch("app.routes.review_routes.ReviewRoutes._get_seeker_id")
    @patch("app.database.get_connection")
    def test_review_page_loads(self, mock_get_connection, mock_get_seeker_id, mock_get_by_id, mock_render):
        mock_get_seeker_id.return_value = 7
        mock_get_by_id.return_value = {"User_id": 5, "First_name": "Jane"}
        mock_get_connection.return_value = make_mock_connection(companies=[{"Employee_id": 10, "Company_name": "Acme"}])
        mock_render.return_value = "reviews_page"

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.get("/reviews")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "reviews_page")
        mock_get_by_id.assert_called_once_with(5)
        mock_get_seeker_id.assert_called_once_with(5)
        mock_render.assert_called_once()

    @patch("app.routes.review_routes.flash")
    def test_review_redirects_when_unauthenticated(self, mock_flash):
        with self.app.test_client() as client:
            response = client.get("/reviews")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)
        mock_flash.assert_called_once_with("Please log in as a job seeker to view company reviews.", "error")

    @patch("app.routes.review_routes.flash")
    @patch("app.routes.review_routes.UserModel.get_by_id")
    @patch("app.routes.review_routes.ReviewRoutes._get_seeker_id")
    def test_review_redirects_when_no_seeker_profile(self, mock_get_seeker_id, mock_get_by_id, mock_flash):
        mock_get_seeker_id.return_value = None
        mock_get_by_id.return_value = {"User_id": 5, "First_name": "Jane"}

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.get("/reviews")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/job-seeker/dashboard", response.location)
        mock_flash.assert_called_once_with("Job seeker profile not found.", "error")

    @patch("app.routes.review_routes.flash")
    @patch("app.routes.review_routes.ReviewController.create_review")
    @patch("app.routes.review_routes.ReviewController.get_reviews_by_employee")
    @patch("app.routes.review_routes.ReviewController.get_review_summary")
    @patch("app.routes.review_routes.UserModel.get_by_id")
    @patch("app.routes.review_routes.ReviewRoutes._get_seeker_id")
    def test_submit_review_success(self, mock_get_seeker_id, mock_get_by_id, mock_get_review_summary, mock_get_reviews, mock_create_review, mock_flash):
        mock_get_seeker_id.return_value = 7
        mock_get_by_id.return_value = {"User_id": 5, "First_name": "Jane"}
        mock_get_review_summary.return_value = {"Average_rating": 4.5}
        mock_get_reviews.return_value = []
        mock_create_review.return_value = True

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.post(
                "/seeker/company-review/10",
                data={"review_text": "Great company", "rating": "5"},
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/seeker/company-review/10", response.location)
        mock_flash.assert_called_once_with("Review submitted successfully.", "success")
        mock_create_review.assert_called_once_with(7, 10, "Great company", 5)

    @patch("app.routes.review_routes.flash")
    @patch("app.routes.review_routes.UserModel.get_by_id")
    @patch("app.routes.review_routes.ReviewRoutes._get_seeker_id")
    def test_submit_review_missing_fields(self, mock_get_seeker_id, mock_get_by_id, mock_flash):
        mock_get_seeker_id.return_value = 7
        mock_get_by_id.return_value = {"User_id": 5, "First_name": "Jane"}

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.post(
                "/seeker/company-review/10",
                data={"review_text": "", "rating": ""},
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/seeker/company-review/10", response.location)
        mock_flash.assert_called_once_with("Please provide both review text and rating.", "error")

    @patch("app.routes.review_routes.flash")
    @patch("app.routes.review_routes.UserModel.get_by_id")
    @patch("app.routes.review_routes.ReviewRoutes._get_seeker_id")
    def test_submit_review_invalid_rating_non_integer(self, mock_get_seeker_id, mock_get_by_id, mock_flash):
        mock_get_seeker_id.return_value = 7
        mock_get_by_id.return_value = {"User_id": 5, "First_name": "Jane"}

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.post(
                "/seeker/company-review/10",
                data={"review_text": "Good", "rating": "bad"},
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/seeker/company-review/10", response.location)
        mock_flash.assert_called_once_with("Rating must be an integer between 1 and 5.", "error")

    @patch("app.routes.review_routes.flash")
    @patch("app.routes.review_routes.UserModel.get_by_id")
    @patch("app.routes.review_routes.ReviewRoutes._get_seeker_id")
    def test_submit_review_invalid_rating_out_of_range(self, mock_get_seeker_id, mock_get_by_id, mock_flash):
        mock_get_seeker_id.return_value = 7
        mock_get_by_id.return_value = {"User_id": 5, "First_name": "Jane"}

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.post(
                "/seeker/company-review/10",
                data={"review_text": "Good", "rating": "10"},
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/seeker/company-review/10", response.location)
        mock_flash.assert_called_once_with("Rating must be between 1 and 5.", "error")

    @patch("app.routes.review_routes.flash")
    @patch("app.routes.review_routes.ReviewController.create_review")
    @patch("app.routes.review_routes.ReviewController.get_reviews_by_employee")
    @patch("app.routes.review_routes.ReviewController.get_review_summary")
    @patch("app.routes.review_routes.UserModel.get_by_id")
    @patch("app.routes.review_routes.ReviewRoutes._get_seeker_id")
    def test_submit_review_failure_from_model(self, mock_get_seeker_id, mock_get_by_id, mock_get_review_summary, mock_get_reviews, mock_create_review, mock_flash):
        mock_get_seeker_id.return_value = 7
        mock_get_by_id.return_value = {"User_id": 5, "First_name": "Jane"}
        mock_get_review_summary.return_value = {}
        mock_get_reviews.return_value = []
        mock_create_review.return_value = False

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.post(
                "/seeker/company-review/10",
                data={"review_text": "Fine", "rating": "4"},
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/seeker/company-review/10", response.location)
        mock_flash.assert_called_once_with("Failed to submit review. Please try again.", "error")

    @patch("app.routes.review_routes.flash")
    def test_edit_review_redirects_with_error(self, mock_flash):
        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.get("/seeker/company-review/10/edit/3")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/seeker/company-review/10", response.location)
        mock_flash.assert_called_once_with("Editing reviews is not allowed. Please submit a new review if needed.", "error")

    @patch("app.routes.review_routes.flash")
    def test_delete_review_redirects_with_error(self, mock_flash):
        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.post("/seeker/company-review/10/delete/3")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/seeker/company-review/10", response.location)
        mock_flash.assert_called_once_with("Deleting reviews is not allowed.", "error")


class TestReviewControllerLogic(unittest.TestCase):
    @patch("app.controllers.review_controller.CompanyReviewModel.create_review")
    def test_create_review(self, mock_create_review):
        mock_create_review.return_value = 21
        result = ReviewController.create_review(7, 10, "Great work", 5)
        self.assertEqual(result, 21)
        mock_create_review.assert_called_once_with(7, 10, "Great work", 5)

    @patch("app.controllers.review_controller.CompanyReviewModel.get_review_by_id")
    def test_get_review(self, mock_get_review):
        mock_get_review.return_value = {"Review_id": 3}
        result = ReviewController.get_review(3)
        self.assertEqual(result, {"Review_id": 3})
        mock_get_review.assert_called_once_with(3)

    @patch("app.controllers.review_controller.CompanyReviewModel.get_review_summary")
    def test_get_review_summary(self, mock_summary):
        mock_summary.return_value = {"Average_rating": 4}
        result = ReviewController.get_review_summary(10, status="Approved")
        self.assertEqual(result, {"Average_rating": 4})
        mock_summary.assert_called_once_with(10, status="Approved")

    @patch("app.controllers.review_controller.CompanyReviewModel.get_reviews_by_employee")
    def test_get_reviews_by_employee(self, mock_reviews):
        mock_reviews.return_value = [{"Review_id": 1}]
        result = ReviewController.get_reviews_by_employee(10, status="Approved")
        self.assertEqual(result, [{"Review_id": 1}])
        mock_reviews.assert_called_once_with(10, status="Approved")

    @patch("app.controllers.review_controller.CompanyReviewModel.get_approved_reviews_by_employee")
    def test_get_approved_reviews_by_employee(self, mock_approved_reviews):
        mock_approved_reviews.return_value = [{"Review_id": 5}]
        result = ReviewController.get_approved_reviews_by_employee(10)
        self.assertEqual(result, [{"Review_id": 5}])
        mock_approved_reviews.assert_called_once_with(10)

    @patch("app.controllers.review_controller.CompanyReviewModel.get_all_reviews_for_admin")
    def test_get_all_reviews_for_admin(self, mock_all_reviews):
        mock_all_reviews.return_value = [{"Review_id": 6}]
        result = ReviewController.get_all_reviews_for_admin()
        self.assertEqual(result, [{"Review_id": 6}])
        mock_all_reviews.assert_called_once()

    @patch("app.controllers.review_controller.CompanyReviewModel.update_review_status")
    def test_update_review_status(self, mock_update_status):
        mock_update_status.return_value = True
        result = ReviewController.update_review_status(3, "Approved")
        self.assertTrue(result)
        mock_update_status.assert_called_once_with(3, "Approved")

    @patch("app.controllers.review_controller.CompanyReviewModel.update_review")
    def test_update_review(self, mock_update_review):
        mock_update_review.return_value = 1
        result = ReviewController.update_review(3, 7, "Updated text", 4)
        self.assertEqual(result, 1)
        mock_update_review.assert_called_once_with(3, 7, "Updated text", 4)

    @patch("app.controllers.review_controller.CompanyReviewModel.delete_review")
    def test_delete_review(self, mock_delete_review):
        mock_delete_review.return_value = 1
        result = ReviewController.delete_review(3, 7)
        self.assertEqual(result, 1)
        mock_delete_review.assert_called_once_with(3, 7)


if __name__ == "__main__":
    unittest.main()
