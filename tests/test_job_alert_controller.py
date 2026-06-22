import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, Blueprint
from app.routes.job_alert_routes import JobAlertRoutes


def make_test_app():
    app = Flask(__name__)
    app.secret_key = "test-secret-key"
    app.register_blueprint(JobAlertRoutes().job_alerts())

    login_bp = Blueprint("login", __name__)
    login_bp.route("/login", endpoint="index")(lambda: "login")
    app.register_blueprint(login_bp)

    return app


def make_valid_session(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 5
        sess["role"] = "job_seeker"


class TestJobAlertControllerRoutes(unittest.TestCase):
    def setUp(self):
        self.app = make_test_app()

    @patch("app.routes.job_alert_routes.render_template")
    @patch("app.routes.job_alert_routes.JobPostingModel.search_jobs_for_seekers")
    @patch("app.routes.job_alert_routes.JobAlertController.list_alerts")
    @patch("app.routes.job_alert_routes.JobSeekerProfileModel.get_profile_by_user_id")
    def test_job_alerts_page_loads(self, mock_get_profile, mock_list_alerts, mock_search_jobs, mock_render):
        mock_get_profile.return_value = {"Seekers_id": 7}
        mock_list_alerts.return_value = [
            {"Notification_id": 1, "Is_active": True, "Keyword": "Python", "Location": "Remote", "Job_type": "Full-time", "Industry": "Tech"}
        ]
        mock_search_jobs.return_value = [{"Job_id": 11}, {"Job_id": 12}]
        mock_render.return_value = "job_alerts_page"

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.get("/job-alerts")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "job_alerts_page")
        mock_get_profile.assert_called_once_with(5)
        mock_list_alerts.assert_called_once_with(7)
        mock_search_jobs.assert_called_once()
        mock_render.assert_called_once()

    @patch("app.routes.job_alert_routes.JobAlertController.create_alert")
    @patch("app.routes.job_alert_routes.JobSeekerProfileModel.get_profile_by_user_id")
    def test_create_alert_success(self, mock_get_profile, mock_create_alert):
        mock_get_profile.return_value = {"Seekers_id": 7}
        mock_create_alert.return_value = 42

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.post(
                "/job-alerts/create",
                data={
                    "keyword": "django",
                    "location": "NYC",
                    "frequency": "daily",
                    "job_type": "Full-time",
                    "industry": "Software",
                    "is_active": "1",
                },
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {"status": "success", "message": "Job alert created successfully."})
        mock_create_alert.assert_called_once_with(7, "django", "NYC", "daily", "Full-time", "Software", True)

    @patch("app.routes.job_alert_routes.JobAlertController.update_alert")
    @patch("app.routes.job_alert_routes.JobSeekerProfileModel.get_profile_by_user_id")
    def test_update_alert_success(self, mock_get_profile, mock_update_alert):
        mock_get_profile.return_value = {"Seekers_id": 7}
        mock_update_alert.return_value = 1

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.post(
                "/job-alerts/update/3",
                data={
                    "keyword": "flask",
                    "location": "Remote",
                    "frequency": "weekly",
                    "job_type": "Part-time",
                    "industry": "IT",
                    "is_active": "0",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "success", "message": "Job alert updated."})
        mock_update_alert.assert_called_once_with(3, 7, "flask", "Remote", "weekly", "Part-time", "IT", False)

    @patch("app.routes.job_alert_routes.JobAlertController.delete_alert")
    @patch("app.routes.job_alert_routes.JobSeekerProfileModel.get_profile_by_user_id")
    def test_delete_alert_success(self, mock_get_profile, mock_delete_alert):
        mock_get_profile.return_value = {"Seekers_id": 7}
        mock_delete_alert.return_value = 1

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.post("/job-alerts/delete/5")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "success", "message": "Job alert deleted."})
        mock_delete_alert.assert_called_once_with(5, 7)

    @patch("app.routes.job_alert_routes.JobSeekerProfileModel.get_profile_by_user_id")
    def test_create_alert_invalid_data(self, mock_get_profile):
        mock_get_profile.return_value = {"Seekers_id": 7}

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.post(
                "/job-alerts/create",
                data={
                    "keyword": "   ",
                    "location": "NYC",
                    "frequency": "daily",
                },
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"status": "error", "message": "Keyword is required."})

    @patch("app.routes.job_alert_routes.JobSeekerProfileModel.get_profile_by_user_id")
    def test_update_alert_invalid_data(self, mock_get_profile):
        mock_get_profile.return_value = {"Seekers_id": 7}

        with self.app.test_client() as client:
            make_valid_session(client)
            response = client.post(
                "/job-alerts/update/5",
                data={
                    "keyword": "",
                    "location": "Remote",
                    "frequency": "weekly",
                },
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"status": "error", "message": "Keyword is required."})

    @patch("app.routes.job_alert_routes.flash")
    def test_redirects_to_login_when_unauthenticated(self, mock_flash):
        with self.app.test_client() as client:
            response = client.get("/job-alerts")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)
        mock_flash.assert_called_once_with("Please log in as a job seeker to manage alerts.", "error")

    @patch("app.routes.job_alert_routes.JobSeekerProfileModel.get_profile_by_user_id")
    def test_delete_alert_not_found_returns_error(self, mock_get_profile):
        mock_get_profile.return_value = {"Seekers_id": 7}

        with patch("app.routes.job_alert_routes.JobAlertController.delete_alert", return_value=0) as mock_delete_alert:
            with self.app.test_client() as client:
                make_valid_session(client)
                response = client.post("/job-alerts/delete/999")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "error", "message": "Alert not found."})
        mock_delete_alert.assert_called_once_with(999, 7)


if __name__ == "__main__":
    unittest.main()
