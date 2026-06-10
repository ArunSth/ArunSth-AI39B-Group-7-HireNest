from app.modals.job_alert import JobAlertModel


class JobAlertController:
    @staticmethod
    def create_alert(seeker_id, keyword, location, frequency, job_type=None, industry=None, is_active=True):
        return JobAlertModel.create_alert(seeker_id, keyword, location, frequency, job_type, industry, is_active)

    @staticmethod
    def list_alerts(seeker_id):
        return JobAlertModel.get_alerts(seeker_id)

    @staticmethod
    def update_alert(alert_id, seeker_id, keyword, location, frequency, job_type=None, industry=None, is_active=True):
        return JobAlertModel.update_alert(alert_id, seeker_id, keyword, location, frequency, job_type, industry, is_active)

    @staticmethod
    def delete_alert(alert_id, seeker_id):
        return JobAlertModel.delete_alert(alert_id, seeker_id)
