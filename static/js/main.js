document.addEventListener('DOMContentLoaded', function() {
    const gallery = document.getElementById('tribute-gallery');
    let page = 1;

    function loadTributes() {
        fetch(`/get_tributes?page=${page}`)
            .then(response => response.json())
            .then(data => {
                data.forEach(tribute => {
                    const div = document.createElement('div');
                    div.className = 'tribute-item';
                    div.innerHTML = `
                        <img src="${tribute.image}" alt="Tribute">
                        <p class="description">${tribute.description}</p>
                    `;
                    gallery.appendChild(div);
                });
                page++;
            });
    }

    // Load more tributes when scrolling to bottom
    window.addEventListener('scroll', () => {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
            loadTributes();
        }
    });

    // Handle form submission on contribute page
    const form = document.getElementById('contribution-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            fetch('/contribute', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Thank you for your contribution!');
                    window.location.href = '/';  // Redirect to home page
                } else {
                    alert(data.message || 'An error occurred. Please try again.');
                }
            });
        });
    }
});