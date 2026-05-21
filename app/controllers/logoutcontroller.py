from flask import render_template


class LogoutController:
    def logout(self):
        return render_template("Logout.html")
