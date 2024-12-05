document.addEventListener('DOMContentLoaded', function () {
    const queryInput = document.getElementById('query');
    const searchButton = document.getElementById('search-button');

    queryInput.addEventListener('input', function () {
        searchButton.disabled = !queryInput.value.trim();
    });
});
