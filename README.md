# DirectAdmin Email Forwarder Manager 📧

A modern web-based interface for managing email forwarders in DirectAdmin. This Docker container provides a clean, user-friendly UI with authentication to create, view, and delete email forwarders without accessing the DirectAdmin control panel directly.

![Docker Pulls](https://img.shields.io/docker/pulls/gittimeraider/directadmin-emailforwarder)
![GitHub Stars](https://img.shields.io/github/stars/gittimeraider/directadmin-emailforwarder)
![License](https://img.shields.io/github/license/gittimeraider/directadmin-emailforwarder)

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
    container_name: directadmin-mailfw
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

