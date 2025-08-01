<p align="center">
  <img src="img/icon_main_25.png" />
</p>

# DirectAdmin Email Forwarder Manager 📧

A modern web-based interface for managing email forwarders in DirectAdmin. This Docker container provides a clean, user-friendly UI with authentication to create, view, and delete email forwarders without accessing the DirectAdmin control panel directly.

## ✨ Features

- **🔐 Secure Web Interface** - Protected with username/password authentication
- **📬 Email Forwarder Management** - Create, view, and delete email forwarders
- **📋 Smart Destination Selection** - Choose from existing email accounts or enter custom addresses
- **🎨 Modern UI** - Clean, responsive design that works on desktop and mobile
- **🔄 Auto-refresh** - Forwarder list updates automatically every 30 seconds
- **👤 User Filtering** - Automatically filters out admin email accounts from destination options
- **🐳 Docker Ready** - Easy deployment with Docker and Docker Compose
- **🔧 Configurable** - All settings managed through environment variables

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. Create a `docker-compose.yml` file:

```yaml
version: 3.8;
services:
  email-forwarder-ui:
    image: ghcr.io/gittimeraider/directadmin-emailforwarder:latest
    container_name: da-mailforward
    ports:
      - 5000:5000
    environment:
      - PUID=1000
      - PGID=1000
      - WEB_USERNAME=admin
      - WEB_PASSWORD=ChangeThisPassword123!
      - SECRET_KEY=your-secret-key-here
      - DA_URL=https://your-directadmin-server.com:2222
      - DA_USER=your_directadmin_username
      - DA_PASS=your_directadmin_password
      - DA_DOMAIN=your-domain.com
    restart: unless-stopped
```

2. Start the container:
```bash
docker-compose up -d
```

3. Access the web interface at `http://localhost:PORTNUMBER`

### Using Docker Run

```bash
docker run -d \
  --name da-mailforward \
  -p 5000:5000 \
  -e PUID=$(id -u) \
  -e PGID=$(id -g) \
  -e WEB_USERNAME=admin \
  -e WEB_PASSWORD=ChangeMe123! \
  -e SECRET_KEY=your-secret-key \
  -e DA_URL=https://your-server.com:2222 \
  -e DA_USER=directadmin_user \
  -e DA_PASS=directadmin_pass \
  -e DA_DOMAIN=yourdomain.com \
  --restart unless-stopped \
  ghcr.io/gittimeraider/directadmin-emailforwarder:latest
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PUID` | User ID for the container process | `1000` | No |
| `PGID` | Group ID for the container process | `1000` | No |
| `WEB_USERNAME` | Username for web UI login | `admin` | Yes* |
| `WEB_PASSWORD` | Password for web UI login | `changeme` | Yes* |
| `SECRET_KEY` | Flask secret key for sessions | Generated | Yes* |
| `DA_URL` | DirectAdmin server URL with port | - | Yes |
| `DA_USER` | DirectAdmin username | - | Yes |
| `DA_PASS` | DirectAdmin password | - | Yes |
| `DA_DOMAIN` | Domain to manage forwarders for | - | Yes |

*\* Should be changed from defaults for security*


## 🔒 Security Considerations

1. **Generate a secure SECRET_KEY instead of making one up**:
```bash
python3 -c &quot;import secrets; print(secrets.token_hex(32))&quot;
```

2. **Use strong passwords** for both web UI and DirectAdmin credentials

3. **Enable HTTPS** in production using a reverse proxy (nginx, Traefik, etc.)

4. **Firewall rules** - Only expose the port  to trusted networks

5. **Keep the image updated** for security patches

## 📝 Usage

### Login
Navigate to `http://your-server:PORT` and login with your configured credentials.

### Creating a Forwarder
1. Enter an alias (e.g., "info", "support", "sales")
2. Select a destination email from the dropdown or choose "Enter custom email address..."
3. Click "Create Forwarder"

### Managing Forwarders
- View all existing forwarders in the list
- Click "Delete" to remove a forwarder
- The list auto-refreshes every 30 seconds

### Features in Detail

**Smart Email Selection**: The destination dropdown automatically populates with existing email accounts from your DirectAdmin domain, filtering out admin accounts for cleaner selection.

**Custom Destinations**: Select the "Enter custom email address..." option to forward to any email address, including external domains.

**Session Management**: Sessions expire after inactivity, automatically redirecting to the login page for security.

## 🐳 Building from Source

If you want to build the image yourself:

```bash
git clone https://github.com/gittimeraider/directadmin-emailforwarder.git
cd directadmin-emailforwarder
docker build -t directadmin-emailforwarder .
```

## 🛠️ Troubleshooting

### Cannot connect to DirectAdmin
- Verify the DA_URL includes the correct protocol and port (usually https://server:2222)
- Check if your DirectAdmin user has email management permissions
- Try accessing the `/api/debug-forwarders` endpoint for raw API responses

### Email accounts not showing in dropdown
- Ensure your DirectAdmin user has permission to list email accounts
- Check that the domain is correctly set in DA_DOMAIN
- Verify the DirectAdmin API is accessible from the container

### Session keeps expiring
- Increase the session timeout by modifying the Flask configuration
- Check that the SECRET_KEY remains consistent between container restarts

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎩 Acknowledgments

- Built with Flask and modern web technologies
- Designed for simplicity and security
- Inspired by the need for easier email forwarder management

---

Made with ☕ and 🎩 by [gittimeraider](https://github.com/gittimeraider)
