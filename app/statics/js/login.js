document.addEventListener('DOMContentLoaded', function () {
    const buttons = Array.from(document.querySelectorAll('.action-button'));

    buttons.forEach((button) => {
        button.addEventListener('click', function () {
            this.classList.add('is-active');
            window.setTimeout(() => this.classList.remove('is-active'), 180);
        });
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            const primaryButton = document.querySelector('.action-button--primary');
            if (primaryButton) {
                primaryButton.classList.add('is-active');
                window.setTimeout(() => primaryButton.classList.remove('is-active'), 180);
            }
        }
    });
});

