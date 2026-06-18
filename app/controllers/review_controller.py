from app.modals.company_review import CompanyReviewModel


class ReviewController:
    @staticmethod
    def create_review(seekers_id, employee_id, review_text, rating):
        return CompanyReviewModel.create_review(seekers_id, employee_id, review_text, rating)

    @staticmethod
    def get_review(review_id):
        return CompanyReviewModel.get_review_by_id(review_id)

    @staticmethod
    def get_review_summary(employee_id):
        return CompanyReviewModel.get_review_summary(employee_id)

    @staticmethod
    def get_reviews_by_employee(employee_id):
        return CompanyReviewModel.get_reviews_by_employee(employee_id)

    @staticmethod
    def update_review(review_id, seekers_id, review_text, rating):
        return CompanyReviewModel.update_review(review_id, seekers_id, review_text, rating)

    @staticmethod
    def delete_review(review_id, seekers_id):
        return CompanyReviewModel.delete_review(review_id, seekers_id)
