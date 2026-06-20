from datetime import datetime

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for, flash

from app.controllers.job_alert_controller import JobAlertController
from app.modals.job_posting_model import JobPostingModel
from app.modals.job_seeker_profile import JobSeekerProfileModel


class JobAlertRoutes:
    def __init__(self):
        self.blueprint = Blueprint('job_alerts', __name__)

    def job_alerts(self):
        @self.blueprint.route('/job-alerts', methods=['GET'])
        def index():
            if 'user_id' not in session or session.get('role') != 'job_seeker':
                flash('Please log in as a job seeker to manage alerts.', 'error')
                return redirect(url_for('login.index'))

            user_id = session['user_id']
            seeker_profile = JobSeekerProfileModel.get_profile_by_user_id(
                user_id)
            alerts = JobAlertController.list_alerts(
                seeker_profile['Seekers_id']) if seeker_profile else []

            matched_alerts = []
            if seeker_profile and alerts:
                for alert in alerts:
                    if alert.get('Is_active'):
                        filters = {
                            'keyword': alert.get('Keyword'),
                            'location': alert.get('Location'),
                            'job_type': alert.get('Job_type') or 'All Types',
                            'industry': alert.get('Industry'),
                        }
                        matches = JobPostingModel.search_jobs_for_seekers(
                            filters, seeker_profile['Seekers_id'])[:3]
                    else:
                        matches = []
                    matched_alerts.append({
                        'alert': alert,
                        'matches': matches,
                        'count': len(matches),
                    })

            return render_template(
                'job_alerts.html',
                alerts=alerts,
                matched_alerts=matched_alerts,
                seeker_profile=seeker_profile,
            )

        @self.blueprint.route('/job-alerts/create', methods=['POST'])
        def create_alert():
            if 'user_id' not in session or session.get('role') != 'job_seeker':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            user_id = session['user_id']
            seeker_profile = JobSeekerProfileModel.get_profile_by_user_id(
                user_id)
            if not seeker_profile:
                return jsonify({'status': 'error', 'message': 'Complete your job seeker profile first.'}), 400

            keyword = request.form.get('keyword', '').strip()
            location = request.form.get('location', '').strip()
            frequency = request.form.get(
                'frequency', 'instant').strip().lower()
            job_type = request.form.get('job_type', '').strip() or None
            industry = request.form.get('industry', '').strip() or None
            is_active = request.form.get('is_active', '1') == '1'

            if not keyword:
                return jsonify({'status': 'error', 'message': 'Keyword is required.'}), 400

            JobAlertController.create_alert(
                seeker_profile['Seekers_id'], keyword, location, frequency, job_type, industry, is_active)
            return jsonify({'status': 'success', 'message': 'Job alert created successfully.'}), 201

        @self.blueprint.route('/job-alerts/update/<int:alert_id>', methods=['POST'])
        def update_alert(alert_id):
            if 'user_id' not in session or session.get('role') != 'job_seeker':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            user_id = session['user_id']
            seeker_profile = JobSeekerProfileModel.get_profile_by_user_id(
                user_id)
            if not seeker_profile:
                return jsonify({'status': 'error', 'message': 'Complete your job seeker profile first.'}), 400

            keyword = request.form.get('keyword', '').strip()
            location = request.form.get('location', '').strip()
            frequency = request.form.get(
                'frequency', 'instant').strip().lower()
            job_type = request.form.get('job_type', '').strip() or None
            industry = request.form.get('industry', '').strip() or None
            is_active = request.form.get('is_active', '1') == '1'

            if not keyword:
                return jsonify({'status': 'error', 'message': 'Keyword is required.'}), 400

            JobAlertController.update_alert(
                alert_id, seeker_profile['Seekers_id'], keyword, location, frequency, job_type, industry, is_active)
            return jsonify({'status': 'success', 'message': 'Job alert updated.'}), 200

        @self.blueprint.route('/job-alerts/delete/<int:alert_id>', methods=['POST'])
        def delete_alert(alert_id):
            if 'user_id' not in session or session.get('role') != 'job_seeker':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            user_id = session['user_id']
            seeker_profile = JobSeekerProfileModel.get_profile_by_user_id(
                user_id)
            if not seeker_profile:
                return jsonify({'status': 'error', 'message': 'Complete your job seeker profile first.'}), 400

            deleted = JobAlertController.delete_alert(
                alert_id, seeker_profile['Seekers_id'])
            return jsonify({'status': 'success' if deleted else 'error', 'message': 'Job alert deleted.' if deleted else 'Alert not found.'}), 200

        return self.blueprint
