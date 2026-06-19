from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app.modals.job_seeker_profile import JobSeekerProfileModel
from app.modals.user import UserModel
from app.modals.interview_scheduling_model import InterviewSchedulingModel
from app.modals.saved_job_model import SavedJobModel
from datetime import datetime
import os
import base64


class JobSeekerRoutes:
    def __init__(self):
        self.blueprint = Blueprint('job_seeker', __name__)

    def register_routes(self):
        """Register all job seeker routes"""
        self.job_seeker_profile()
        return self.blueprint

    def job_seeker_dashboard(self):
        @self.blueprint.route('/job-seeker/dashboard', methods=['GET'])
        def dashboard():
            if 'user_id' not in session or session.get('role') != 'job_seeker':
                flash('Please log in as a job seeker to view your dashboard.', 'error')
                return redirect(url_for('login.index'))

            user_id = session['user_id']
            JobSeekerProfileModel.ensure_profile_exists(user_id)
            user_data = UserModel.get_by_id(user_id)
            profile_data = JobSeekerProfileModel.get_profile_by_user_id(user_id)
            completion_percentage = JobSeekerProfileModel.calculate_profile_completion(user_id)

            return render_template(
                'seeker_dashboard.html',
                user=user_data,
                profile=profile_data,
                completion_percentage=completion_percentage
            )

    def job_seeker_profile(self):

        @self.blueprint.route('/job-seeker/profile', methods=['GET', 'POST'])
        def profile():
            if 'user_id' not in session or session.get('role') != 'job_seeker':
                flash('Please log in as a job seeker to view your profile.', 'error')
                return redirect(url_for('login.index'))

            user_id = session['user_id']
            JobSeekerProfileModel.ensure_profile_exists(user_id)
            user_data = UserModel.get_by_id(user_id)
            profile_data = JobSeekerProfileModel.get_profile_by_user_id(user_id)
            completion_percentage = JobSeekerProfileModel.calculate_profile_completion(user_id)

            if request.method == 'POST':
                bio = request.form.get('bio', '').strip()
                location = request.form.get('location', '').strip()
                education = request.form.get('education', '').strip()
                skills = request.form.get('skills', '').strip()
                experiences = request.form.get('experiences', '').strip()

                if JobSeekerProfileModel.create_or_update_profile(user_id, bio, location, education, skills, experiences):
                    new_completion_percentage = JobSeekerProfileModel.calculate_profile_completion(user_id)
                    JobSeekerProfileModel.update_profile_completion(user_id, new_completion_percentage)
                    flash('Profile updated successfully!', 'success')
                    return redirect(url_for('job_seeker.profile'))
                else:
                    flash('Failed to update profile. Please try again.', 'error')

            return render_template(
                'job_seeker_profile.html',
                user=user_data,
                profile=profile_data,
                completion_percentage=completion_percentage
            )

        @self.blueprint.route('/job-seeker/dashboard', methods=['GET'])
        def dashboard():
            if 'user_id' not in session or session.get('role') != 'job_seeker':
                flash('Please log in as a job seeker to view your dashboard.', 'error')
                return redirect(url_for('login.index'))

            user_id = session['user_id']
            user_data = UserModel.get_by_id(user_id)
            profile_data = JobSeekerProfileModel.get_profile_by_user_id(user_id)
            completion_percentage = JobSeekerProfileModel.calculate_profile_completion(user_id)

            from app.database import get_connection
            conn = get_connection()
            applications = []
            interviews = []
            profile_incomplete = False
            try:
                with conn.cursor() as cur:
                    cur.execute('SELECT `Seekers_id` FROM `Job_Seekers` WHERE `User_id`=%s', (user_id,))
                    seeker = cur.fetchone()
                    if not seeker:
                        profile_incomplete = True
                    else:
                        seekers_id = seeker['Seekers_id']
                        cur.execute(
                            '''
                            SELECT 
                                a.`Application_id`,
                                a.`Status`,
                                a.`Applied_at`,
                                j.`Title` AS job_title,
                                j.`Salary`,
                                j.`Location`,
                                e.`Company_name`
                            FROM `Applications` a
                            JOIN `Jobs` j ON a.`Job_id` = j.`Job_id`
                            JOIN `Employee` e ON j.`Employee_id` = e.`Employee_id`
                            WHERE a.`Seekers_id`=%s
                            ORDER BY a.`Applied_at` DESC
                            ''',
                            (seekers_id,),
                        )
                        applications = cur.fetchall()
                        interviews = InterviewSchedulingModel.get_interviews_for_applicant(seekers_id)
            finally:
                conn.close()

            applied_count = len(applications)
            rejected_count = sum(1 for app in applications if app.get('Status', '').lower() == 'rejected')
            alerts_count = sum(1 for interview in interviews if interview.get('Status', '').lower() == 'scheduled')
            bookmarks_count = SavedJobModel.count_saved_jobs(seekers_id) if not profile_incomplete else 0
            recent_applications = applications[:4]

            recent_activities = []
            for app in applications[:3]:
                recent_activities.append({
                    'title': f"Applied to {app.get('job_title', 'Job')}",
                    'subtitle': f"{app.get('Company_name', 'Company')} • {app.get('Status', 'Pending').title()}",
                    'time': app['Applied_at'].strftime('%d %b %Y') if app.get('Applied_at') else 'N/A'
                })

            for interview in interviews[:2]:
                recent_activities.append({
                    'title': f"Interview {interview.get('Status', 'Scheduled').title()}",
                    'subtitle': f"{interview.get('job_title', 'Position')} at {interview.get('Company_name', '')}",
                    'time': interview['Interview_date'].strftime('%d %b') if interview.get('Interview_date') else 'N/A'
                })

            profile_alert_title = 'Complete your profile'
            profile_alert_text = 'Update your profile and location details to improve your job matches.'
            profile_action_text = 'Complete Profile'

            if profile_data and completion_percentage == 100:
                profile_alert_title = 'Profile complete'
                profile_alert_text = 'Your job seeker profile looks great. Keep applying to new jobs.'
                profile_action_text = 'View Profile'

            return render_template(
                'seeker_dashboard.html',
                user=user_data,
                profile=profile_data,
                completion_percentage=completion_percentage,
                applied_count=applied_count,
                alerts_count=alerts_count,
                rejected_count=rejected_count,
                bookmarks_count=bookmarks_count,
                recent_applications=recent_applications,
                recent_activities=recent_activities,
                profile_alert_title=profile_alert_title,
                profile_alert_text=profile_alert_text,
                profile_action_text=profile_action_text,
                profile_incomplete=profile_incomplete
            )

        @self.blueprint.route('/job-seeker/profile/photo', methods=['POST'])
        def upload_photo():
            if 'user_id' not in session or session.get('role') != 'job_seeker':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            user_id = session['user_id']

            if 'photo' not in request.files:
                return jsonify({'status': 'error', 'message': 'No photo file provided'}), 400

            photo_file = request.files['photo']
            if photo_file.filename == '':
                return jsonify({'status': 'error', 'message': 'No file selected'}), 400

            allowed_ext = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
            ext = photo_file.filename.rsplit('.', 1)[-1].lower() if '.' in photo_file.filename else ''
            if ext not in allowed_ext:
                return jsonify({'status': 'error', 'message': 'Only JPG, PNG, WEBP, GIF files are accepted'}), 400

            photo_bytes = photo_file.read()
            if len(photo_bytes) > 5 * 1024 * 1024:
                return jsonify({'status': 'error', 'message': 'Photo must be under 5MB'}), 400

            upload_folder = os.path.join(os.getcwd(), 'app', 'statics', 'uploads', 'photos')
            os.makedirs(upload_folder, exist_ok=True)
            filename = f"photo_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
            filepath = os.path.join(upload_folder, filename)
            with open(filepath, 'wb') as f:
                f.write(photo_bytes)

            if JobSeekerProfileModel.update_photo(user_id, filename):
                return jsonify({'status': 'success', 'message': 'Photo uploaded!', 'filename': filename}), 200
            else:
                return jsonify({'status': 'error', 'message': 'Failed to save photo'}), 500

        @self.blueprint.route('/job-seeker/profile/resume', methods=['POST'])
        def upload_resume():
            if 'user_id' not in session or session.get('role') != 'job_seeker':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            user_id = session['user_id']

            if 'resume' not in request.files:
                return jsonify({'status': 'error', 'message': 'No resume file provided'}), 400

            resume_file = request.files['resume']
            if resume_file.filename == '':
                return jsonify({'status': 'error', 'message': 'No selected file'}), 400

            if resume_file and self._allowed_resume_file(resume_file.filename):
                upload_folder = os.path.join(os.getcwd(), 'uploads', 'resumes')
                os.makedirs(upload_folder, exist_ok=True)
                filename = f"resume_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{resume_file.filename.rsplit('.', 1)[1].lower()}"
                filepath = os.path.join(upload_folder, filename)
                resume_file.save(filepath)

                if JobSeekerProfileModel.update_resume(user_id, filename, datetime.now()):
                    new_pct = JobSeekerProfileModel.calculate_profile_completion(user_id)
                    JobSeekerProfileModel.update_profile_completion(user_id, new_pct)
                    return jsonify({'status': 'success', 'message': 'Resume uploaded successfully!', 'filename': filename}), 200
                else:
                    return jsonify({'status': 'error', 'message': 'Failed to save resume path to database'}), 500
            else:
                return jsonify({'status': 'error', 'message': 'Invalid file type. Accepted: PDF, DOCX (max 10MB)'}), 400

        @self.blueprint.route('/job-seeker/profile/resume/delete', methods=['POST'])
        def delete_resume():
            if 'user_id' not in session or session.get('role') != 'job_seeker':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            user_id = session['user_id']
            profile_data = JobSeekerProfileModel.get_profile_by_user_id(user_id)

            if profile_data and profile_data.get('Resume'):
                resume_filename = profile_data['Resume']
                filepath = os.path.join(os.getcwd(), 'uploads', 'resumes', resume_filename)
                if os.path.exists(filepath):
                    os.remove(filepath)

                if JobSeekerProfileModel.delete_resume(user_id):
                    new_pct = JobSeekerProfileModel.calculate_profile_completion(user_id)
                    JobSeekerProfileModel.update_profile_completion(user_id, new_pct)
                    return jsonify({'status': 'success', 'message': 'Resume deleted successfully!'}), 200
                else:
                    return jsonify({'status': 'error', 'message': 'Failed to delete resume from database'}), 500
            else:
                return jsonify({'status': 'error', 'message': 'No resume found to delete'}), 404

        return self.blueprint

    def _allowed_resume_file(self, filename):
        if '.' not in filename:
            return False

        if filename.rsplit('.', 1)[1].lower() not in ['pdf', 'docx']:
            return False

        content_length = request.content_length
        if content_length is not None and content_length > 10 * 1024 * 1024:
            return False

        return True
