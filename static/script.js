// Authentication-aware request wrapper
async function makeAuthenticatedRequest(url, options = {}) {
    const response = await fetch(url, options);

    // If we get a redirect to login, the session expired
    if (response.redirected && response.url.includes('/login')) {
        window.location.href = '/login';
        return null;
    }

    return response;
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('forwarder-form');
    const messageDiv = document.getElementById('message');
    const forwardersList = document.getElementById('forwarders-list');

    // Load existing forwarders on page load
    loadForwarders();

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const alias = document.getElementById('alias').value;
        const destination = document.getElementById('destination').value;

        try {
            const response = await makeAuthenticatedRequest('/api/create-forwarder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ alias, destination })
            });

            if (!response) return; // Redirected to login

            const data = await response.json();

            if (data.success) {
                showMessage(data.message, 'success');
                form.reset();
                loadForwarders(); // Reload the list
            } else {
                showMessage(data.error || 'Failed to create forwarder', 'error');
            }
        } catch (error) {
            showMessage('Network error: ' + error.message, 'error');
        }
    });

    // Load and display forwarders
    async function loadForwarders() {
        try {
            forwardersList.innerHTML = '<p class="loading">Loading forwarders...</p>';

            const response = await makeAuthenticatedRequest('/api/forwarders');
            if (!response) return; // Redirected to login

            const data = await response.json();

            if (data.success) {
                displayForwarders(data.forwarders);
            } else {
                forwardersList.innerHTML = '<p class="error">Failed to load forwarders</p>';
            }
        } catch (error) {
            console.error('Error loading forwarders:', error);
            forwardersList.innerHTML = '<p class="error">Network error</p>';
        }
    }

    // Display forwarders in the list
    function displayForwarders(forwarders) {
        if (!forwarders || forwarders.length === 0) {
            forwardersList.innerHTML = '<p>No forwarders configured yet.</p>';
            return;
        }

        forwardersList.innerHTML = forwarders.map(forwarder => {
            // Handle multiple destinations
            const destinationsHtml = forwarder.destinations.map(dest => 
                `<div class="forwarder-destination">→ ${dest}</div>`
            ).join('');

            return `
                <div class="forwarder-item">
                    <div class="forwarder-info">
                        <div class="forwarder-alias">${forwarder.alias}@${getDomain()}</div>
                        ${destinationsHtml}
                    </div>
                    <button class="btn btn-danger" onclick="deleteForwarder('${forwarder.alias}')">
                        Delete
                    </button>
                </div>
            `;
        }).join('');
    }

    // Get domain from environment or default
    function getDomain() {
        return window.DA_DOMAIN || 'your-domain.com';
    }

    // Delete forwarder
    window.deleteForwarder = async function(alias) {
        if (!confirm(`Delete forwarder ${alias}@${getDomain()}?`)) return;

        try {
            const response = await makeAuthenticatedRequest('/api/delete-forwarder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ alias })
            });

            if (!response) return; // Redirected to login

            const data = await response.json();

            if (data.success) {
                showMessage(data.message, 'success');
                loadForwarders();
            } else {
                showMessage(data.error || 'Failed to delete forwarder', 'error');
            }
        } catch (error) {
            showMessage('Network error: ' + error.message, 'error');
        }
    };

    // Show message
    function showMessage(text, type) {
        messageDiv.textContent = text;
        messageDiv.className = `message ${type} show`;

        setTimeout(() => {
            messageDiv.classList.remove('show');
        }, 3000);
    }

    // Auto-refresh forwarders every 30 seconds
    setInterval(() => {
        loadForwarders();
    }, 30000);

    // Handle session timeout gracefully
    document.addEventListener('click', function(e) {
        // If clicking on debug button, also check authentication
        if (e.target.matches('.btn-secondary')) {
            makeAuthenticatedRequest('/api/debug-forwarders')
                .then(response => {
                    if (!response) {
                        e.preventDefault();
                        return;
                    }
                    // Continue with normal behavior
                });
        }
    });
});

// Global error handler for unexpected logouts
window.addEventListener('unhandledrejection', function(event) {
    if (event.reason && event.reason.message && event.reason.message.includes('login')) {
        window.location.href = '/login';
    }
});
