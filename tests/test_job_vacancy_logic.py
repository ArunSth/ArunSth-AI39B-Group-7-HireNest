from app.modals.job_posting_model import JobPostingModel


def test_calculate_vacancy_metrics():
    metrics = JobPostingModel.calculate_vacancy_metrics(3, 1)
    assert metrics["total_vacancies"] == 3
    assert metrics["filled_vacancies"] == 1
    assert metrics["remaining_vacancies"] == 2
    assert metrics["is_filled"] is False


def test_calculate_vacancy_metrics_when_filled():
    metrics = JobPostingModel.calculate_vacancy_metrics(2, 2)
    assert metrics["remaining_vacancies"] == 0
    assert metrics["is_filled"] is True
