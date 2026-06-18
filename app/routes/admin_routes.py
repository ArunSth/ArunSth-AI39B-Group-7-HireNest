from flask import Blueprint, jsonify, request, session, render_template, redirect, url_for
from app.modals.admin_profile import AdminProfileModel
from app.modals.job_posting_model import JobPostingModel
from app.modals.user import UserModel
 
 
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
 
        # ── 4. Profile API ────────────────────────────────────
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
 
        # ── 5. Audit Logs API ─────────────────────────────────
        @self.blueprint.route('/admin/audit-logs', methods=['GET'])
        def audit_logs():
            if 'user_id' not in session or session.get('role') != 'admin':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
 
            limit = request.args.get('limit', 50, type=int)
            logs  = AdminProfileModel.get_audit_logs(
                admin_user_id=session['user_id'], limit=limit
            )
            return jsonify({'status': 'success', 'audit_logs': logs}), 200
 
        # ── 6. Send Announcement ──────────────────────────────
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
                    # Fetch target users based on audience selection
                    if audience == 'all':
                        cur.execute(
                            "SELECT `User_id` FROM `User` WHERE `Role` IN ('Job Seeker', 'Employer')"
                        )
                    else:
                        cur.execute(
                            "SELECT `User_id` FROM `User` WHERE `Role` = %s",
                            (audience,)
                        )
                    users = cur.fetchall()
 
                    if not users:
                        return jsonify({
                            'status':     'success',
                            'message':    'No matching users found.',
                            'recipients': 0,
                        })
 
                    # Bulk-insert one notification row per recipient
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
 
                # Record in audit log
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
 
        return self.blueprint
 