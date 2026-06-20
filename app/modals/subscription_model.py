import json
from datetime import date, datetime, timedelta
from app.database import get_connection


class SubscriptionModel:
    @staticmethod
    def ensure_default_plans():
        plans = SubscriptionModel.get_all_plans()
        if plans:
            return

        default_features = [
            ["5 job posts", "Basic employer support"],
            ["15 job posts", "Priority posting"],
            ["Unlimited job posts", "Premium support"]
        ]

        default_data = [
            ("Free", "Limited access for small teams.", 0.00, "monthly",
             1, json.dumps(["1 job post", "Community support"])),
            ("Basic", "Starter plan for small teams.", 29.99,
             "monthly", 5, json.dumps(default_features[0])),
            ("Growth", "Expanded visibility and more job posts.",
             59.99, "monthly", 15, json.dumps(default_features[1])),
            ("Premium", "Unlimited posting plus premium support.",
             99.99, "monthly", 0, json.dumps(default_features[2])),
        ]

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                for plan_name, description, price, billing_cycle, max_posts, features in default_data:
                    cur.execute(
                        """
                        INSERT INTO `Subscription_Plans` (`Plan_name`, `Description`, `Price`, `Billing_cycle`, `Max_job_posts`, `Features_json`)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (plan_name, description, price,
                         billing_cycle, max_posts, features),
                    )
                conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_all_plans():
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM `Subscription_Plans`
                    WHERE Is_active = TRUE
                    ORDER BY Price ASC
                    """
                )
                plans = cur.fetchall()
                for plan in plans:
                    if plan.get("Features_json"):
                        try:
                            plan["Features"] = json.loads(
                                plan["Features_json"])
                        except Exception:
                            plan["Features"] = []
                    else:
                        plan["Features"] = []
                return plans
        finally:
            conn.close()

    @staticmethod
    def get_plan_by_id(plan_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM `Subscription_Plans` WHERE Plan_id = %s", (
                        plan_id,)
                )
                plan = cur.fetchone()
                if plan and plan.get("Features_json"):
                    try:
                        plan["Features"] = json.loads(plan["Features_json"])
                    except Exception:
                        plan["Features"] = []
                elif plan:
                    plan["Features"] = []
                return plan
        finally:
            conn.close()

    @staticmethod
    def get_subscription_by_id(subscription_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM `Employer_Subscriptions` WHERE Subscription_id = %s", (
                        subscription_id,)
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_active_subscription(employee_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT s.*, p.Plan_name, p.Price, p.Billing_cycle, p.Max_job_posts, p.Features_json
                    FROM `Employer_Subscriptions` s
                    JOIN `Subscription_Plans` p ON s.Plan_id = p.Plan_id
                    WHERE s.Employee_id = %s AND s.Status = 'active'
                    ORDER BY s.Start_date DESC
                    LIMIT 1
                    """,
                    (employee_id,),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def deactivate_active_subscription(employee_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE `Employer_Subscriptions` SET Status = 'cancelled' WHERE Employee_id = %s AND Status = 'active'",
                    (employee_id,),
                )
                conn.commit()
                return cur.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def cancel_subscription(subscription_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE `Employer_Subscriptions` SET Status = 'cancelled' WHERE Subscription_id = %s",
                    (subscription_id,),
                )
                conn.commit()
                return cur.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def update_subscription_status(subscription_id, status):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE `Employer_Subscriptions` SET Status = %s WHERE Subscription_id = %s",
                    (status, subscription_id),
                )
                conn.commit()
                return cur.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def get_subscriptions_by_employee(employee_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT s.*, p.Plan_name, p.Price, p.Billing_cycle
                    FROM `Employer_Subscriptions` s
                    JOIN `Subscription_Plans` p ON s.Plan_id = p.Plan_id
                    WHERE s.Employee_id = %s
                    ORDER BY s.Start_date DESC
                    """,
                    (employee_id,),
                )
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def create_subscription(employee_id, plan_id, start_date, end_date, auto_renew=False):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO `Employer_Subscriptions` (`Employee_id`, `Plan_id`, `Start_date`, `End_date`, `Status`, `Auto_renew`)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (employee_id, plan_id, start_date,
                     end_date, 'active', auto_renew),
                )
                conn.commit()
                return cur.lastrowid
        finally:
            conn.close()

    @staticmethod
    def record_payment(subscription_id, employee_id, amount, currency='USD', payment_method='card', transaction_reference=None, status='paid'):
        payment_time = datetime.now()

        if transaction_reference is None:
            transaction_reference = f"txn_{payment_time.strftime('%Y%m%d%H%M%S%f')}"

        paid_at = payment_time.strftime('%Y-%m-%d %H:%M:%S')
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO `Payment_History` (`Subscription_id`, `Employee_id`, `Amount`, `Currency`, `Payment_method`, `Transaction_reference`, `Status`, `Paid_at`)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (subscription_id, employee_id, amount, currency,
                     payment_method, transaction_reference, status, paid_at),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error recording payment: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def get_payment_history(employee_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT ph.*, p.Plan_name, p.Billing_cycle
                    FROM `Payment_History` ph
                    LEFT JOIN `Employer_Subscriptions` s ON ph.Subscription_id = s.Subscription_id
                    LEFT JOIN `Subscription_Plans` p ON s.Plan_id = p.Plan_id
                    WHERE ph.Employee_id = %s
                    ORDER BY ph.Paid_at DESC
                    """,
                    (employee_id,),
                )
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_payment_by_id(payment_id):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT ph.*, p.Plan_name, p.Billing_cycle "
                    "FROM `Payment_History` ph "
                    "LEFT JOIN `Employer_Subscriptions` s ON ph.Subscription_id = s.Subscription_id "
                    "LEFT JOIN `Subscription_Plans` p ON s.Plan_id = p.Plan_id "
                    "WHERE ph.Payment_id = %s",
                    (payment_id,),
                )
                return cur.fetchone()
        finally:
            conn.close()
