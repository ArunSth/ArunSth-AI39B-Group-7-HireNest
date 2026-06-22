from flask import request, session, flash, redirect, url_for


class BaseController:
    def get_form_data(self, *fields):
        return tuple(request.form.get(field, "") for field in fields)

    def is_logged_in(self):
        return bool(session.get("user_id"))

    def get_current_user_id(self):
        return session.get("user_id")

    def flash_and_redirect(self, message, category, endpoint):
        flash(message, category)
        return redirect(url_for(endpoint))
