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
    const destinationSelect = document.getElementById('destination-select');
    const customDestinationWrapper = document.getElementById('custom-destination-wrapper');
    const customDestinationInput = document.getElementById('custom-destination');

    // Load existing forwarders and email accounts on page load
    loadForwarders();
    loadEmailAccounts();

    // Handle destination select change
    destinationSelect.addEventListener('change', function() {
        if (this.value === 'custom') {
            customDestinationWrapper.style.display = 'block';
            customDestinationInput.required = true;
            customDestinationInput.focus();
        } else {
            customDestinationWrapper.style.display = 'none';
            customDestinationInput.required = false;
            customDestinationInput.value = '';
        }
    });

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const alias = document.getElementById('alias').value;
        let destination = destinationSelect.value;

        // If custom is selected, use the custom input value
        if (destination === 'custom') {
            destination = customDestinationInput.value;
            if (!destination) {
                showMessage('Please enter a custom email address', 'error');
                return;
            }
        }

        if (!destination) {
            showMessage('Please select a destination email', 'error');
            return;
        }

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
                customDestinationWrapper.style.display = 'none';
                loadForwarders(); // Reload the list
                loadEmailAccounts(); // Reload email accounts
            } else {
                showMessage(data.error || 'Failed to create forwarder', 'error');
            }
        } catch (error) {
            showMessage('Network error: ' + error.message, 'error');
        }
    });

    // Load email accounts for the dropdown
    async function loadEmailAccounts() {
        try {
            const response = await makeAuthenticatedRequest('/api/email-accounts');
            if (!response) return;

            const data = await response.json();

            if (data.success) {
                populateDestinationSelect(data.accounts);
            } else {
                console.error('Failed to load email accounts');
                // Fallback to just custom option
                populateDestinationSelect([]);
            }
        } catch (error) {
            console.error('Error loading email accounts:', error);
            populateDestinationSelect([]);
        }
    }

    // Populate the destination select dropdown
    function populateDestinationSelect(accounts) {
        destinationSelect.innerHTML = '';

        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = '-- Select destination email --';
        destinationSelect.appendChild(defaultOption);

        // Add email accounts
        if (accounts && accounts.length > 0) {
            const accountsGroup = document.createElement('optgroup');
            accountsGroup.label = 'Existing Email Accounts';

            accounts.forEach(account => {
                const option = document.createElement('option');
                option.value = account;
                option.textContent = account;
                accountsGroup.appendChild(option);
            });

            destinationSelect.appendChild(accountsGroup);
        }

        // Add separator
        if (accounts && accounts.length > 0) {
            const separator = document.createElement('option');
            separator.disabled = true;
            separator.textContent = '────────────────';
            destinationSelect.appendChild(separator);
        }

        // Add custom option
        const customOption = document.createElement('option');
        customOption.value = 'custom';
        customOption.textContent = '✏️ Enter custom email address...';
        destinationSelect.appendChild(customOption);
    }

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
