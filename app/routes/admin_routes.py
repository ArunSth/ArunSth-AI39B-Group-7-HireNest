from flask import Blueprint, jsonify, request, session, render_template, redirect, url_for
from app.modals.admin_profile import AdminProfileModel
from app.modals.job_posting_model import JobPostingModel
from app.modals.user import UserModel
from app.modals.notification import NotificationModel
 
 
class AdminRoutes:
    def __init__(self):
        self.blueprint = Blueprint('admin', __name__)
 
    def register_routes(self):
 
        # ── 1. Dashboard ──────────────────────────────────────
        @self.blueprint.route('/admin/dashboard', methods=['GET'])
        def admin_dashboard():
            if 'user_id' not in session or session.get('role') != 'admin':
                return redirect(url_for('login.login_page'))
 
            user_id     = session['user_id']
            profile     = AdminProfileModel.get_profile_by_user_id(user_id)
            completion  = AdminProfileModel.calculate_profile_completion(user_id)
            recent_logs = AdminProfileModel.get_audit_logs(admin_user_id=user_id, limit=5)
            users       = UserModel.get_all_users()
 
            stats = {
                'total_users':        UserModel.get_total_users(),
                'active_jobs':        JobPostingModel.get_active_jobs(),
                'total_applications': 0,
                'total_reports':      0,
            }
 
            return render_template(
                'admin_dashboard.html',
                profile=profile,
                completion=completion,
                logs=recent_logs,
                stats=stats,
                users=users,
            )
 
        # ── 2. Add User ───────────────────────────────────────
        @self.blueprint.route('/admin/users/add', methods=['POST'])
        def add_user():
            if 'user_id' not in session or session.get('role') != 'admin':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
 
            data       = request.get_json(silent=True) or {}
            first_name = data.get('firstName', '').strip()
            last_name  = data.get('lastName',  '').strip()
            email      = data.get('email',     '').strip()
            password   = data.get('password',  '').strip()
            role       = data.get('role',      'job_seeker')
 
            if not first_name or not email or not password:
                return jsonify({'status': 'error', 'message': 'Name, email and password are required.'}), 400
 
            if UserModel.get_by_email(email):
                return jsonify({'status': 'error', 'message': 'A user with this email already exists.'}), 400
 
            try:
                UserModel.create(email, password, first_name, last_name, role)
                new_user = UserModel.get_by_email(email)
                return jsonify({
                    'status': 'success',
                    'user': { 'id': new_user['User_id'] if new_user else None }
                })
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
 
        # ── 3. Delete User ────────────────────────────────────
        @self.blueprint.route('/admin/users/<int:user_id>/delete', methods=['POST'])
        def delete_user(user_id):
            if 'user_id' not in session or session.get('role') != 'admin':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
 
            from app.database import get_connection
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM `User` WHERE `User_id`=%s", (user_id,))
                conn.commit()
                return jsonify({'status': 'success'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
            finally:
                conn.close()
 
        # ── 4. Delete Moderation Job ──────────────────────────
        # ── 4. Delete Moderation Job ──────────────────────────
        @self.blueprint.route('/admin/moderation/jobs/<int:job_id>/delete', methods=['POST'])
        def delete_moderation_job(job_id):
            if 'user_id' not in session or session.get('role') != 'admin':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    # fetch BEFORE deleting — you need owner + title after the row is gone
            job = JobPostingModel.get_job_by_id(job_id)
            if not job:
                return jsonify({'status': 'error', 'message': 'Job not found.'}), 404

            success = JobPostingModel.delete_job(job_id)
            if not success:
                return jsonify({'status': 'error', 'message': 'Failed to delete job.'}), 500

            AdminProfileModel.record_audit_log(
                session['user_id'], 'job_deleted', 'job', job_id,
                f'Job #{job_id} deleted by admin.'
            )

            NotificationModel.create_notification(
                user_id=job['Employer_id'],   # <-- confirm actual column name
                title='Job Posting Removed',
                message=f'Your job posting "{job["Title"]}" was removed by an administrator.',
                notification_type='job_deleted',
                reference_id=job_id,
            )

            return jsonify({'status': 'success'})
 
       
        # ── 6. Reject Job ─────────────────────────────────────
        @self.blueprint.route('/admin/moderation/jobs/<int:job_id>/reject', methods=['POST'])
        def reject_job(job_id):
            if 'user_id' not in session or session.get('role') != 'admin':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            success = JobPostingModel.update_job_status(job_id, 'Rejected')
            if not success:
                return jsonify({'status': 'error', 'message': 'Failed to reject job.'}), 500

            job = JobPostingModel.get_job_by_id(job_id)
            title = job['Title'] if job else f'Job #{job_id}'

            AdminProfileModel.record_audit_log(
                session['user_id'], 'job_rejected', 'job', job_id,
                f'Job "{title}" rejected — hidden from job seekers.'
            )

            if job:
                NotificationModel.create_notification(
                    user_id=job['Employer_id'],   # <-- confirm actual column name
                    title='Job Posting Rejected',
                    message=f'Your job posting "{title}" was rejected by an administrator.',
                    notification_type='job_rejected',
                    reference_id=job_id,
                )

            return jsonify({
                'status':  'success',
                'message': f'"{title}" rejected and hidden from job seekers.',
            })
 
        # ── 7. List Jobs for Moderation Panel ─────────────────
        @self.blueprint.route('/admin/moderation/jobs', methods=['GET'])
        def moderation_jobs():
            if 'user_id' not in session or session.get('role') != 'admin':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
 
            jobs = JobPostingModel.get_all_jobs_for_admin()
            result = []
            for j in jobs:
                db_status = (j['Status'] or '').lower()
                # Map DB values → UI labels shown in the admin panel
                if db_status == 'approved':
                    ui_status = 'Approved'
                elif db_status == 'rejected':
                    ui_status = 'Rejected'
                else:
                    ui_status = 'Pending'   # covers 'pending' and anything unexpected
 
                result.append({
                    'id':          j['Job_id'],
                    'title':       j['Title'],
                    'company':     j['Company_name'],
                    'type':        j['Job_type'],
                    'location':    j['Location'],
                    'status':      ui_status,
                    'submitted':   j['Created_at'].strftime('%#d %b %Y') if j['Created_at'] else '—',
                    'description': j['Description'] or '',
                    'logo':        j['Logo'] if j.get('Logo') else None,
                })
            return jsonify(result)
 
        # ── 8. Profile API ────────────────────────────────────
        @self.blueprint.route('/admin/profile', methods=['GET', 'POST'])
        def profile():
            if 'user_id' not in session or session.get('role') != 'admin':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
 
            user_id        = session['user_id']
            user_data      = UserModel.get_by_id(user_id)
            profile_data   = AdminProfileModel.get_profile_by_user_id(user_id)
            completion_pct = AdminProfileModel.calculate_profile_completion(user_id)
 
            if request.method == 'POST':
                payload      = request.get_json(silent=True) or request.form
                display_name = (payload.get('display_name') or '').strip() or None
                department   = (payload.get('department')   or '').strip() or None
                access_level = (payload.get('access_level') or 'full').strip()
                bio          = (payload.get('bio')          or '').strip() or None
                is_active    = str(payload.get('is_active', True)).lower() not in ('0', 'false', 'no')
 
                if not display_name or not department:
                    return jsonify({'status': 'error', 'message': 'Display name and department are required.'}), 400
 
                if AdminProfileModel.create_or_update_profile(
                    user_id, display_name, department, access_level, bio, is_active
                ):
                    completion = AdminProfileModel.calculate_profile_completion(user_id)
                    AdminProfileModel.update_profile_completion(user_id, completion)
                    AdminProfileModel.update_last_login(user_id)
                    AdminProfileModel.record_audit_log(
                        user_id, 'updated_profile', 'admin_profile', user_id,
                        'Admin profile was updated.'
                    )
                    return jsonify({
                        'status':                'success',
                        'message':               'Admin profile updated successfully.',
                        'profile':               AdminProfileModel.get_profile_by_user_id(user_id),
                        'completion_percentage': completion,
                    }), 200
 
                return jsonify({'status': 'error', 'message': 'Failed to update admin profile.'}), 500
 
            recent_logs = AdminProfileModel.get_audit_logs(admin_user_id=user_id, limit=10)
            return jsonify({
                'status':                'success',
                'user':                  user_data,
                'profile':               profile_data,
                'completion_percentage': completion_pct,
                'recent_audit_logs':     recent_logs,
            }), 200
 
        # ── 9. Audit Logs API ─────────────────────────────────
        @self.blueprint.route('/admin/audit-logs', methods=['GET'])
        def audit_logs():
            if 'user_id' not in session or session.get('role') != 'admin':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
 
            limit = request.args.get('limit', 50, type=int)
            logs  = AdminProfileModel.get_audit_logs(
                admin_user_id=session['user_id'], limit=limit
            )
            return jsonify({'status': 'success', 'audit_logs': logs}), 200
 
        # ── 10. Send Announcement ─────────────────────────────
        @self.blueprint.route('/admin/announcements/send', methods=['POST'])
        def send_announcement():
            if 'user_id' not in session or session.get('role') != 'admin':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
 
            data     = request.get_json(silent=True) or {}
            subject  = data.get('subject',  '').strip()
            message  = data.get('message',  '').strip()
            audience = data.get('audience', 'all').strip()
 
            if not subject or not message:
                return jsonify({'status': 'error', 'message': 'Subject and message are required.'}), 400
 
            from app.database import get_connection
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    if audience == 'all':
                        cur.execute("SELECT `User_id` FROM `User`")
                    elif audience == 'Job Seeker':
                        cur.execute("SELECT `User_id` FROM `User` WHERE `Role` = 'job_seeker'")
                    elif audience == 'Employer':
                        cur.execute("SELECT `User_id` FROM `User` WHERE `Role` = 'employer'")
                    else:
                        cur.execute("SELECT `User_id` FROM `User` WHERE `Role` = %s", (audience,))
                    users = cur.fetchall()
 
                    if not users:
                        return jsonify({
                            'status':     'success',
                            'message':    'No matching users found.',
                            'recipients': 0,
                        })
 
                    cur.executemany(
                        """
                        INSERT INTO `Notification`
                            (`User_id`, `Title`, `Message`, `Is_read`, `Created_at`)
                        VALUES
                            (%s, %s, %s, 0, NOW())
                        """,
                        [
                            (u['User_id'], f"📢 {subject}", message)
                            for u in users
                        ]
                    )
 
                conn.commit()
 
                AdminProfileModel.record_audit_log(
                    session['user_id'],
                    'sent_announcement',
                    'notification',
                    None,
                    f'Announcement "{subject}" sent to {len(users)} user(s) [{audience}].'
                )
 
                return jsonify({
                    'status':     'success',
                    'message':    f'Announcement sent to {len(users)} user(s).',
                    'recipients': len(users),
                })
 
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
            finally:
                conn.close()

        
        # ── 11. Save Settings ─────────────────────────────────
        @self.blueprint.route('/admin/settings/save', methods=['POST'])
        def save_admin_settings():
            if 'user_id' not in session or session.get('role') != 'admin':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            from flask import current_app
            from app.database import get_connection
 
            data = request.get_json(silent=True) or {}
            print(f"DEBUG SAVE: received data = {data}")

            settings = {
                'userRegistration':     data.get('userRegistration',     True),
                'employerVerification': data.get('employerVerification', False),
                'autoApproveJobs':      data.get('autoApproveJobs',      False),
                'jobModeration':        data.get('jobModeration',         True),
                'emailAlerts':          data.get('emailAlerts',           True),
                'weeklyReports':        data.get('weeklyReports',         False),
            }

            print(f"DEBUG SAVE: settings = {settings}")

    # Update app.config immediately
            current_app.config['ADMIN_SETTINGS'] = settings

    # Save to DB so it survives restarts
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    for key, value in settings.items():
                        cur.execute("""
                           INSERT INTO `AdminSettings` (`key`, `value`)
                           VALUES (%s, %s)
                           ON DUPLICATE KEY UPDATE `value` = VALUES(`value`)
                           """, (key, '1' if value else '0'))
                conn.commit()
                print("DEBUG SAVE: DB write successful")
            except Exception as e:
                print(f"DEBUG SAVE: DB write FAILED = {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
            finally:
               conn.close()

    # Auto-approve pending jobs if toggled on
            if settings.get('autoApproveJobs'):
                conn2 = get_connection()
                try:
                    with conn2.cursor() as cur:
                        cur.execute(
                            "UPDATE `Job_posting` SET `Status` = 'approved' WHERE `Status` = 'pending'"
                        )
                    conn2.commit()
                except Exception:
                    pass
                finally:
                    conn2.close()

            AdminProfileModel.record_audit_log(
                session['user_id'], 'settings_updated', 'admin_settings', None,
                f"Registration:{settings['userRegistration']} "
                f"AutoApprove:{settings['autoApproveJobs']} "
                f"Moderation:{settings['jobModeration']}"
            )

            return jsonify({'status': 'success'})
 
        @self.blueprint.route('/admin/settings/load', methods=['GET'])
        def load_admin_settings():
            if 'user_id' not in session or session.get('role') != 'admin':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            from flask import current_app
            settings = current_app.config.get('ADMIN_SETTINGS', {
                'userRegistration':     True,
                'employerVerification': False,
                'autoApproveJobs':      False,
                'jobModeration':        True,
                'emailAlerts':          True,
                'weeklyReports':        False,
            })
            return jsonify({'status': 'success', 'settings': settings})
        
        return self.blueprint
 