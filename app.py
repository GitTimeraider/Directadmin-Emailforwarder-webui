import os
import requests
from flask import Flask, render_template, request, jsonify
from requests.auth import HTTPBasicAuth
import urllib3
from urllib.parse import unquote

# Disable SSL warnings if needed (use with caution)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Configuration from environment variables
DIRECTADMIN_URL = os.environ.get('DA_URL', 'https://your-server.com:2222')
DIRECTADMIN_USER = os.environ.get('DA_USER', 'admin')
DIRECTADMIN_PASS = os.environ.get('DA_PASS', 'password')
DOMAIN = os.environ.get('DA_DOMAIN', 'example.com')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/forwarders', methods=['GET'])
def get_forwarders():
    """Get existing forwarders from DirectAdmin"""
    try:
        response = requests.post(
            f"{DIRECTADMIN_URL}/CMD_API_EMAIL_FORWARDERS",
            auth=HTTPBasicAuth(DIRECTADMIN_USER, DIRECTADMIN_PASS),
            data={'domain': DOMAIN},
            verify=False  # Set to True in production with proper SSL
        )

        if response.status_code == 200:
            # Parse DirectAdmin response
            forwarders = []
            raw_response = response.text.strip()

            # DirectAdmin returns URL-encoded data separated by &
            if raw_response and raw_response != 'error=1':
                # Split by & to get individual forwarder entries
                entries = raw_response.split('&')

                for entry in entries:
                    if '=' in entry and not entry.startswith('error='):
                        # URL decode and split the entry
                        decoded_entry = unquote(entry)
                        parts = decoded_entry.split('=', 1)

                        if len(parts) == 2:
                            alias = parts[0]
                            destinations = parts[1]

                            # Clean up the alias (remove domain if present)
                            if '@' in alias:
                                alias = alias.split('@')[0]

                            # Split multiple destinations if they exist
                            if ',' in destinations:
                                dest_list = [d.strip() for d in destinations.split(',')]
                            else:
                                dest_list = [destinations.strip()]

                            forwarders.append({
                                'alias': alias,
                                'destinations': dest_list,
                                'destinations_str': ', '.join(dest_list)
                            })

            return jsonify({'success': True, 'forwarders': forwarders})
        else:
            return jsonify({'success': False, 'error': 'Failed to fetch forwarders'}), 500
    except Exception as e:
        print(f"Error fetching forwarders: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/create-forwarder', methods=['POST'])
def create_forwarder():
    """Create a new email forwarder"""
    data = request.json
    alias = data.get('alias')
    destination = data.get('destination')

    if not alias or not destination:
        return jsonify({'success': False, 'error': 'Missing alias or destination'}), 400

    try:
        # DirectAdmin API call to create forwarder
        response = requests.post(
            f"{DIRECTADMIN_URL}/CMD_API_EMAIL_FORWARDERS",
            auth=HTTPBasicAuth(DIRECTADMIN_USER, DIRECTADMIN_PASS),
            data={
                'action': 'create',
                'domain': DOMAIN,
                'user': alias,
                'email': destination
            },
            verify=False  # Set to True in production with proper SSL
        )

        if response.status_code == 200 and 'error=0' in response.text:
            return jsonify({'success': True, 'message': f'Forwarder {alias}@{DOMAIN} → {destination} created!'})
        else:
            error_msg = response.text if response.text else 'Unknown error'
            return jsonify({'success': False, 'error': f'DirectAdmin API error: {error_msg}'}), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete-forwarder', methods=['POST'])
def delete_forwarder():
    """Delete an email forwarder"""
    data = request.json
    alias = data.get('alias')

    if not alias:
        return jsonify({'success': False, 'error': 'Missing alias'}), 400

    try:
        response = requests.post(
            f"{DIRECTADMIN_URL}/CMD_API_EMAIL_FORWARDERS",
            auth=HTTPBasicAuth(DIRECTADMIN_USER, DIRECTADMIN_PASS),
            data={
                'action': 'delete',
                'domain': DOMAIN,
                'select0': alias
            },
            verify=False
        )

        if response.status_code == 200 and 'error=0' in response.text:
            return jsonify({'success': True, 'message': f'Forwarder {alias}@{DOMAIN} deleted!'})
        else:
            return jsonify({'success': False, 'error': 'Failed to delete forwarder'}), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
