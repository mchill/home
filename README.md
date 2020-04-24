# Home Server

This is the configuration for my home server.

## Configuration

Set the following environment variables used by Docker Compose.

Variable             | Description
---                  | ---
DUCKDNS_TOKEN        | DuckDNS API token (https://www.duckdns.org/)
GOOGLE_CLIENT_ID     | Google Oauth client ID (https://console.developers.google.com/apis/credentials)
GOOGLE_CLIENT_SECRET | Google Oauth client secret (https://console.developers.google.com/apis/credentials)
OAUTH_SECRET         | A secret used for authentication, can be any string
OPENVPN_USERNAME     | OpenVPN provider username
OPENVPN_PASSWORD     | OpenVPN provider password
PLEX_CLAIM           | Only needed for first time container setup (https://www.plex.tv/claim/)

Create the following local file structure which will be mounted as volumes. The entire directory will be backed up to cloud storage.

```
/data/server             # Mounted in the SFTP server
  acme.json              # Ensure file permission 0600
  keys/                  # Public keys generated for the server
    ssh_host_ed25519_key
    ssh_host_rsa_key
  filestash/
    config.json          # Persisted configs
  qbittorrent/
    config/              # Persisted configs
    downloads/           # Downloaded torrent files
  plex/
    config/              # Persisted configs
    data/                # Hosted media
  minecraft/             # MineCraft world
```

## Usage

Traefik, Portainer, Filestash, and qBittorrent are secured behind Google forward authentication.

Service           | URL
---               | ---
Traefik Dashboard | https://mchill.duckdns.org
Portainer         | https://portainer.mchill.duckdns.org
Filestash         | https://files.mchill.duckdns.org
qBittorrent       | https://torrent.mchill.duckdns.org
Plex              | https://plex.mchill.duckdns.org
SFTP              | mchill.duckdns.org:2222
MineCraft         | mchill.duckdns.org:25565

## To Install

1. Home Assistant
2. rclone
3. Traefik Metrics
