from app.modals.subscription_model import SubscriptionModel


class SubscriptionController:
    @staticmethod
    def ensure_default_plans():
        return SubscriptionModel.ensure_default_plans()

    @staticmethod
    def get_all_plans():
        return SubscriptionModel.get_all_plans()

    @staticmethod
    def get_plan_by_id(plan_id):
        return SubscriptionModel.get_plan_by_id(plan_id)

    @staticmethod
    def get_active_subscription(employee_id):
        return SubscriptionModel.get_active_subscription(employee_id)

    @staticmethod
    def create_subscription(employee_id, plan_id, start_date, end_date, auto_renew=False):
        return SubscriptionModel.create_subscription(employee_id, plan_id, start_date, end_date, auto_renew)

    @staticmethod
    def record_payment(subscription_id, employee_id, amount, payment_method='card', transaction_reference=None, status='paid'):
        return SubscriptionModel.record_payment(subscription_id, employee_id, amount, payment_method=payment_method, transaction_reference=transaction_reference, status=status)

    @staticmethod
    def get_payment_history(employee_id):
        return SubscriptionModel.get_payment_history(employee_id)

    @staticmethod
    def get_payment_by_id(payment_id):
        return SubscriptionModel.get_payment_by_id(payment_id)

    @staticmethod
    def cancel_subscription(subscription_id):
        return SubscriptionModel.cancel_subscription(subscription_id)

    @staticmethod
    def update_subscription_status(subscription_id, status):
        return SubscriptionModel.update_subscription_status(subscription_id, status)