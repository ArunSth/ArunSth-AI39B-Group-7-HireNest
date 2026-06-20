from app.modals.user import UserModel


class ForgetpasswordController:

    @staticmethod
    def check_email(email: str):
        user = UserModel.get_by_email(email)
        if user:
            return True, user
        return False, None

    @staticmethod
    def reset_password(email: str, new_password: str, confirm_password: str):
        if not new_password or not confirm_password:
            return False, 'Please fill in all fields.'
        if new_password != confirm_password:
            return False, 'Passwords do not match.'
        if len(new_password) < 8:
            return False, 'Password must be at least 8 characters long.'
        user = UserModel.get_by_email(email)
        if not user:
            return False, 'No account found with this email.'
        success = UserModel.update_password(email, new_password)
        if success:
            return True, 'Password reset successfully!'
        return False, 'Something went wrong. Please try again.'