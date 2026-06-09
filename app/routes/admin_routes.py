from flask import Blueprint, jsonify, request, session

from app.modals.admin_profile import AdminProfileModel
from app.modals.user import UserModel


class AdminRoutes:
    def __init__(self):
        self.blueprint = Blueprint('admin', __name__)

    def admin_profile(self):
        @self.blueprint.route('/admin/profile', methods=['GET', 'POST'])
        def profile():
            if 'user_id' not in session or session.get('role') != 'admin':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            user_id = session['user_id']
            user_data = UserModel.get_by_id(user_id)
            profile_data = AdminProfileModel.get_profile_by_user_id(user_id)
            completion_percentage = AdminProfileModel.calculate_profile_completion(
                user_id)

            if request.method == 'POST':
                payload = request.get_json(silent=True) or request.form
                display_name = (payload.get('display_name')
                                or '').strip() or None
                department = (payload.get('department') or '').strip() or None
                access_level = (payload.get('access_level')
                                or 'full').strip() or 'full'
                bio = (payload.get('bio') or '').strip() or None
                is_active_raw = payload.get('is_active', True)
                is_active = str(is_active_raw).lower() not in (
                    '0', 'false', 'no')

                if not display_name or not department:
                    return jsonify({'status': 'error', 'message': 'Display name and department are required.'}), 400

                if AdminProfileModel.create_or_update_profile(
                    user_id,
                    display_name,
                    department,
                    access_level=access_level,
                    bio=bio,
                    is_active=is_active,
                ):
                    completion_percentage = AdminProfileModel.calculate_profile_completion(
                        user_id)
                    AdminProfileModel.update_profile_completion(
                        user_id, completion_percentage)
                    AdminProfileModel.update_last_login(user_id)
                    AdminProfileModel.record_audit_log(
                        user_id,
                        'updated_profile',
                        'admin_profile',
                        user_id,
                        'Admin profile was updated.',
                    )
                    profile_data = AdminProfileModel.get_profile_by_user_id(
                        user_id)
                    return jsonify({
                        'status': 'success',
                        'message': 'Admin profile updated successfully.',
                        'profile': profile_data,
                        'completion_percentage': completion_percentage,
                    }), 200

                return jsonify({'status': 'error', 'message': 'Failed to update admin profile.'}), 500

            recent_logs = AdminProfileModel.get_audit_logs(
                admin_user_id=user_id, limit=10)
            return jsonify({
                'status': 'success',
                'user': user_data,
                'profile': profile_data,
                'completion_percentage': completion_percentage,
                'recent_audit_logs': recent_logs,
            }), 200

        @self.blueprint.route('/admin/audit-logs', methods=['GET'])
        def audit_logs():
            if 'user_id' not in session or session.get('role') != 'admin':
                return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

            limit = request.args.get('limit', 50, type=int)
            logs = AdminProfileModel.get_audit_logs(
                admin_user_id=session['user_id'], limit=limit)
            return jsonify({'status': 'success', 'audit_logs': logs}), 200

        return self.blueprint
