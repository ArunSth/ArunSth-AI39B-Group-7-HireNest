from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.controllers.subscription_controller import SubscriptionController
from app.modals.user import UserModel


class SubscriptionRoutes:
    def __init__(self):
        self.blueprint = Blueprint("subscriptions", __name__)

    def subscription_routes(self):
        @self.blueprint.route("/employer/subscription-plans", methods=["GET", "POST"])
        def plans():
            if "user_id" not in session or session.get("role") != "employer":
                flash("Please log in as an employer to view subscription plans.", "error")
                return redirect(url_for("login.index"))

            SubscriptionController.ensure_default_plans()
            user_data = UserModel.get_by_id(session["user_id"])
            plans = SubscriptionController.get_all_plans()
            active_subscription = None

            from app.database import get_connection
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT `Employee_id` FROM `Employee` WHERE `User_id`=%s", (session["user_id"],))
                    employee = cur.fetchone()
                    if employee:
                        employee_id = employee["Employee_id"]
                        active_subscription = SubscriptionController.get_active_subscription(employee_id)
                    else:
                        flash("Employer profile not found.", "error")
                        return redirect(url_for("employer.profile"))
            finally:
                conn.close()

            if request.method == "POST":
                plan_id = request.form.get("plan_id")
                auto_renew = request.form.get("auto_renew") == "on"
                if not plan_id:
                    flash("Please select a plan.", "error")
                    return redirect(url_for("subscriptions.plans"))

                plan = SubscriptionController.get_plan_by_id(plan_id)
                if not plan:
                    flash("Selected plan not found.", "error")
                    return redirect(url_for("subscriptions.plans"))

                from datetime import datetime, timedelta
                start_date = request.form.get("start_date")
                if not start_date:
                    start_date = datetime.utcnow().date()
                else:
                    start_date = datetime.strptime(str(start_date), "%Y-%m-%d").date()

                end_date = request.form.get("end_date")
                if not end_date:
                    end_date = start_date + timedelta(days=30)
                else:
                    end_date = datetime.strptime(str(end_date), "%Y-%m-%d").date()

                if active_subscription:
                    SubscriptionController.cancel_subscription(active_subscription["Subscription_id"])

                subscription_id = SubscriptionController.create_subscription(employee_id, plan_id, start_date, end_date, auto_renew)
                if subscription_id:
                    SubscriptionController.record_payment(subscription_id, employee_id, plan["Price"], transaction_reference=None)
                    flash("Subscription purchased successfully.", "success")
                    return redirect(url_for("subscriptions.plans"))

                flash("Failed to purchase subscription. Please try again.", "error")

            return render_template(
                "subscription_plans.html",
                user=user_data,
                plans=plans,
                active_subscription=active_subscription,
            )

        @self.blueprint.route("/subscription-plans", methods=["GET"])
        def subscription_plans_shortcut():
            return redirect(url_for("subscriptions.plans"))

        @self.blueprint.route("/payment-history", methods=["GET"])
        def payment_history_shortcut():
            return redirect(url_for("subscriptions.payment_history"))

        @self.blueprint.route("/employer/subscription-plans/cancel", methods=["POST"])
        def cancel_subscription():
            if "user_id" not in session or session.get("role") != "employer":
                flash("Please log in as an employer to cancel subscriptions.", "error")
                return redirect(url_for("login.index"))

            from app.database import get_connection
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT `Employee_id` FROM `Employee` WHERE `User_id`=%s", (session["user_id"],))
                    employee = cur.fetchone()
                    if not employee:
                        flash("Employer profile not found.", "error")
                        return redirect(url_for("employer.profile"))
                    active_subscription = SubscriptionController.get_active_subscription(employee["Employee_id"])
            finally:
                conn.close()

            if not active_subscription:
                flash("No active subscription to cancel.", "error")
                return redirect(url_for("subscriptions.plans"))

            if SubscriptionController.cancel_subscription(active_subscription["Subscription_id"]):
                flash("Subscription cancelled successfully.", "success")
            else:
                flash("Failed to cancel subscription. Please try again.", "error")

            return redirect(url_for("subscriptions.plans"))

        @self.blueprint.route("/employer/payment-history", methods=["GET"])
        def payment_history():
            if "user_id" not in session or session.get("role") != "employer":
                flash("Please log in as an employer to view payment history.", "error")
                return redirect(url_for("login.index"))

            user_data = UserModel.get_by_id(session["user_id"])
            from app.database import get_connection
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT `Employee_id` FROM `Employee` WHERE `User_id`=%s", (session["user_id"],))
                    employee = cur.fetchone()
                    if not employee:
                        flash("Employer profile not found.", "error")
                        return redirect(url_for("employer.profile"))
                    payments = SubscriptionController.get_payment_history(employee["Employee_id"])
            finally:
                conn.close()

            return render_template(
                "payment_history.html",
                user=user_data,
                payments=payments,
            )

        @self.blueprint.route("/employer/payment-history/<int:payment_id>/invoice", methods=["GET"])
        def invoice(payment_id):
            if "user_id" not in session or session.get("role") != "employer":
                flash("Please log in as an employer to view invoices.", "error")
                return redirect(url_for("login.index"))

            from app.database import get_connection
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT `Employee_id` FROM `Employee` WHERE `User_id`=%s", (session["user_id"],))
                    employee = cur.fetchone()
                    if not employee:
                        flash("Employer profile not found.", "error")
                        return redirect(url_for("employer.profile"))
                    employee_id = employee["Employee_id"]
                    payment = SubscriptionController.get_payment_by_id(payment_id)
            finally:
                conn.close()

            if not payment or payment.get("Employee_id") != employee_id:
                flash("Invoice not found.", "error")
                return redirect(url_for("subscriptions.payment_history"))

            return render_template("invoice.html", payment=payment)

        return self.blueprint
