import os
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from requests.auth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash
import urllib3
from urllib.parse import unquote
from functools import wraps

# Disable SSL warnings if needed (use with caution)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-this')

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please login to access this page.'

# Configuration from environment variables
DIRECTADMIN_URL = os.environ.get('DA_URL', 'https://your-server.com:2222')
DIRECTADMIN_USER = os.environ.get('DA_USER', 'admin')
DIRECTADMIN_PASS = os.environ.get('DA_PASS', 'password')
DOMAIN = os.environ.get('DA_DOMAIN', 'example.com')

# Web UI Authentication
WEB_USERNAME = os.environ.get('WEB_USERNAME', 'admin')
WEB_PASSWORD = os.environ.get('WEB_PASSWORD', 'changeme')

# Simple user class
class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username

@login_manager.user_loader
def load_user(username):
    if username == WEB_USERNAME:
        return User(username)
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == WEB_USERNAME and password == WEB_PASSWORD:
            user = User(username)
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html', domain=DOMAIN, username=current_user.username)

@app.route('/api/email-accounts', methods=['GET'])
@login_required
def get_email_accounts():
    """Get all email accounts from DirectAdmin"""
    try:
        # First, get all email accounts for the domain
        response = requests.post(
            f"{DIRECTADMIN_URL}/CMD_API_POP",
            auth=HTTPBasicAuth(DIRECTADMIN_USER, DIRECTADMIN_PASS),
            data={
                'domain': DOMAIN,
                'action': 'list'
            },
            verify=False
        )

        email_accounts = []

        if response.status_code == 200:
            raw_response = response.text.strip()
            print(f"DEBUG: Email accounts raw response: {raw_response}")

            if raw_response and 'error=' not in raw_response:
                # DirectAdmin returns list in format: account1&account2&account3
                decoded_response = unquote(raw_response)

                # Handle different possible formats
                if 'list[]=' in decoded_response:
                    # Format: list[]=account1&list[]=account2
                    import re
                    accounts = re.findall(r'list\[\]=([^&]+)', decoded_response)
                else:
                    # Simple format: account1&account2&account3
                    accounts = decoded_response.split('&')

                for account in accounts:
                    account = account.strip()
                    if account and account != 'error=0':
                        # Filter out accounts containing the DirectAdmin username
                        if DIRECTADMIN_USER.lower() not in account.lower():
                            email_accounts.append(f"{account}@{DOMAIN}")

        # Also try to get aliases/forwarders that might be destinations
        try:
            alias_response = requests.post(
                f"{DIRECTADMIN_URL}/CMD_API_EMAIL_FORWARDERS",
                auth=HTTPBasicAuth(DIRECTADMIN_USER, DIRECTADMIN_PASS),
                data={'domain': DOMAIN},
                verify=False
            )

            if alias_response.status_code == 200:
                raw = alias_response.text.strip()
                if raw and 'error=' not in raw:
                    decoded = unquote(raw)
                    entries = decoded.split('&')

                    for entry in entries:
                        if '=' in entry and not entry.startswith('error='):
                            parts = entry.split('=', 1)
                            if len(parts) == 2:
                                destinations = parts[1].strip()
                                # Add unique destination emails
                                if ',' in destinations:
                                    for dest in destinations.split(','):
                                        dest = dest.strip()
                                        if '@' in dest and dest not in email_accounts:
                                            if DIRECTADMIN_USER.lower() not in dest.lower():
                                                email_accounts.append(dest)
                                elif '@' in destinations and destinations not in email_accounts:
                                    if DIRECTADMIN_USER.lower() not in destinations.lower():
                                        email_accounts.append(destinations)
        except:
            pass  # If we can't get forwarders, just continue with email accounts

        # Sort the email accounts
        email_accounts.sort()

        return jsonify({
            'success': True, 
            'accounts': email_accounts,
            'count': len(email_accounts)
        })

    except Exception as e:
        print(f"Error fetching email accounts: {str(e)}")
        return jsonify({'success': False, 'error': str(e), 'accounts': []}), 500

@app.route('/api/forwarders', methods=['GET'])
@login_required
def get_forwarders():
    """Get existing forwarders from DirectAdmin"""
    try:
        response = requests.post(
            f"{DIRECTADMIN_URL}/CMD_API_EMAIL_FORWARDERS",
            auth=HTTPBasicAuth(DIRECTADMIN_USER, DIRECTADMIN_PASS),
            data={'domain': DOMAIN},
            verify=False
        )

        if response.status_code == 200:
            forwarders = []
            raw_response = response.text.strip()

            print(f"DEBUG: Raw response: {raw_response}")

            if not raw_response or raw_response == 'error=1' or raw_response == '':
                return jsonify({'success': True, 'forwarders': []})

            decoded_response = unquote(raw_response)
            entries = decoded_response.split('&')

            for entry in entries:
                if '=' in entry and not entry.startswith('error='):
                    parts = entry.split('=', 1)

                    if len(parts) == 2:
                        alias = parts[0].strip()
                        destinations = parts[1].strip()

                        if '@' in alias:
                            alias = alias.split('@')[0]

                        if ',' in destinations:
                            dest_list = [d.strip() for d in destinations.split(',')]
                        else:
                            dest_list = [destinations]

                        if alias and destinations:
                            forwarders.append({
                                'alias': alias,
                                'destinations': dest_list,
                                'destinations_str': ', '.join(dest_list)
                            })

            return jsonify({'success': True, 'forwarders': forwarders})
        else:
            return jsonify({'success': False, 'error': f'HTTP {response.status_code}'}), 500
    except Exception as e:
        print(f"Error fetching forwarders: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/create-forwarder', methods=['POST'])
@login_required
def create_forwarder():
    """Create a new email forwarder"""
    data = request.json
    alias = data.get('alias')
    destination = data.get('destination')

    if not alias or not destination:
        return jsonify({'success': False, 'error': 'Missing alias or destination'}), 400

    try:
        response = requests.post(
            f"{DIRECTADMIN_URL}/CMD_API_EMAIL_FORWARDERS",
            auth=HTTPBasicAuth(DIRECTADMIN_USER, DIRECTADMIN_PASS),
            data={
                'action': 'create',
                'domain': DOMAIN,
                'user': alias,
                'email': destination
            },
            verify=False
        )

        if response.status_code == 200 and 'error=0' in response.text:
            return jsonify({'success': True, 'message': f'Forwarder {alias}@{DOMAIN} → {destination} created!'})
        else:
            error_msg = response.text if response.text else 'Unknown error'
            return jsonify({'success': False, 'error': f'DirectAdmin API error: {error_msg}'}), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete-forwarder', methods=['POST'])
@login_required
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

@app.route('/api/debug-forwarders', methods=['GET'])
@login_required
def debug_forwarders():
    """Debug endpoint to see raw API response"""
    try:
        response = requests.post(
            f"{DIRECTADMIN_URL}/CMD_API_EMAIL_FORWARDERS",
            auth=HTTPBasicAuth(DIRECTADMIN_USER, DIRECTADMIN_PASS),
            data={'domain': DOMAIN},
            verify=False
        )

        forwarders = []
        raw = response.text.strip()
        decoded = unquote(raw)

        if decoded and decoded != 'error=1':
            entries = decoded.split('&')
            for entry in entries:
                if '=' in entry and not entry.startswith('error='):
                    forwarders.append(entry)

        return jsonify({
            'status_code': response.status_code,
            'raw_response': raw,
            'decoded_response': decoded,
            'split_entries': forwarders,
            'headers': dict(response.headers)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
