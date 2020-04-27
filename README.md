# Home Server

This is the configuration for my home server.

## Configuration

All traffic is routed through Traefik, so only the entrypoints listed in traefik.yml need to be opened on the router. The plex container maps some more ports to the host, but only for the purpose of local server detection.

Set the following environment variables.

Variable                       | Description
---                            | ---
TOKEN                          | DuckDNS API token (https://www.duckdns.org/)
PROVIDERS_GOOGLE_CLIENT_ID     | Google Oauth client ID (https://console.developers.google.com/apis/credentials)
PROVIDERS_GOOGLE_CLIENT_SECRET | Google Oauth client secret (https://console.developers.google.com/apis/credentials)
SECRET                         | Internal OAuth secret
VPN_USERNAME                   | OpenVPN provider username
VPN_PASSWORD                   | OpenVPN provider password
PLEX_CLAIM                     | Plex claim token needed for first time container setup (https://www.plex.tv/claim/)
JICOFO_COMPONENT_SECRET        | Internal Jitsi secret
JICOFO_AUTH_PASSWORD           | Internal Jitsi password
JVB_AUTH_PASSWORD              | Internal Jitsi password

Create the following local file structure which will be mounted as volumes. The entire directory will be backed up to cloud storage.

```
/data/server             # Mounted in the SFTP server
  acme.json              # Ensure file permission 0600
  keys/                  # Public keys generated for the server
    ssh_host_ed25519_key
    ssh_host_rsa_key
  filestash/
    config.json          # Persisted configs
  jitsi/                 # Persisted configs
    /web
    /prosody
    /jicofo
    /jvb
  qbittorrent/
    config/              # Persisted configs
    downloads/           # Downloaded torrent files
  plex/
    config/              # Persisted configs
    data/                # Hosted media
  minecraft/             # Minecraft world
```

## Usage

Traefik, Portainer, Filestash, and qBittorrent are secured behind Google forward authentication. Plex, Jitsi, and Minecraft handle their own authentication.

Service           | URL
---               | ---
Traefik Dashboard | https://mchill.duckdns.org
Portainer         | https://portainer.mchill.duckdns.org
Filestash         | https://files.mchill.duckdns.org
qBittorrent       | https://torrent.mchill.duckdns.org
Plex              | https://plex.mchill.duckdns.org
Jitsi             | https://jitsi.mchill.duckdns.org
SFTP              | mchill.duckdns.org:2222
Minecraft         | mchill.duckdns.org:25565

## To Install

1. Home Assistant
2. rclone
3. Traefik Metrics
