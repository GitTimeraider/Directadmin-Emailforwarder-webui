# Directadmin-Emailforwarder
An webui made for Docker to connect to the Directadmin API and either add or remove Forwarders (mostly used for aliases) in the Email Manager.

# Features: 
- Login page
- Option to either add or remove forwarders
- List of currently existing forwarders


version: '3.8'

services:
  email-forwarder-ui:
    image: ghcr.io/gittimeraider/directadmin-emailforwarder:latest
    container_name: email-forwarder-ui
    ports:
      - "5000:5000"
    environment:
      - PUID=1000
      - PGID=1000
      - WEB_USERNAME=admin
      - WEB_PASSWORD=ChangeThisPassword123!
      - SECRET_KEY=generate-a-random-secret-key-here
      - DA_URL=https://your-directadmin-server.com:2222
      - DA_USER=your_directadmin_username
      - DA_PASS=your_directadmin_password
      - DA_DOMAIN=your-domain.com
    restart: unless-stopped
