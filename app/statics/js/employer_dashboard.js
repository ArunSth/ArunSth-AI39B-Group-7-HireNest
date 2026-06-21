document.addEventListener('DOMContentLoaded', function () {
    // Initialize tooltips and popovers
    initializeEventListeners();
    loadCharts();
});

function initializeEventListeners() {
    // Status update via AJAX
    document.querySelectorAll('[data-status-update]').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = this.dataset.id;
            const newStatus = this.dataset.status;
            const type = this.dataset.type; // 'job', 'application', 'interview'

            updateStatus(id, newStatus, type);
        });
    });

    // Form validation
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

function updateStatus(id, status, type) {
    const endpoint = {
        'job': `/employer/jobs/${id}/status`,
        'application': `/employer/applicant/${id}/status`,
        'interview': `/employer/interview/${id}/status`
    }[type];

    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: status })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showNotification('Success', data.message, 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showNotification('Error', data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error', 'An error occurred', 'error');
        });
}

function validateForm(form) {
    let isValid = true;
    form.querySelectorAll('[required]').forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('error');
            isValid = false;
        } else {
            field.classList.remove('error');
        }
    });
    return isValid;
}

function showNotification(title, message, type) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <strong>${title}</strong>
        <p>${message}</p>
    `;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function loadCharts() {
    // Placeholder for chart initialization
    // Can be extended with Chart.js or similar library
}
