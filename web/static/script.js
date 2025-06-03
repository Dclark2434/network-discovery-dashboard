document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const loading = document.getElementById('loading');
    if (form) {
        form.addEventListener('submit', function () {
            if (loading) {
                loading.style.display = 'flex';
            }
        });
    }
});
