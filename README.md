# Home Server

This is the configuration for my home server.

[Trello Board](https://trello.com/b/XNVnSBvI/home-server)

## Configuration

### Network

All HTTP traffic is routed through Traefik, but TCP and UDP connections are directly exposed to the host. Although additional routers and services could be configured to handle these connections, it adds no benefit other than load balancing due to the lack of host or path matching.

Because Pihole must expose ports 80 and 443 to work properly, HTTP and HTTPS traffic is forwarded to host ports 8080 and 4433, respectively.

The following ports need to be fowarded by your router (TCP unless otherwise noted).

External   | Internal  | Service
---        | ---       | ---
80         | 8080      | HTTP
443        | 4433      | HTTPS
2222       | 2222      | SFTP
25565      | 25565     | Minecraft
4443       | 4443      | Jitsi
10000/udp  | 10000/udp | Jitsi

### Filesystem

Create the following local file structure which will be mounted as volumes. The entire directory will be backed up to cloud storage.

```
/data/server             # Mounted in the SFTP server
  acme.json              # Ensure file permission 0600
  keys/                  # Public keys generated for the server
    ssh_host_ed25519_key
    ssh_host_rsa_key
  prometheus/            # Collected data
  filestash/             # Persisted configs
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

### Environment

Set the following environment variables.

Variable                       | Description
---                            | ---
DUCKDNS_TOKEN                  | DuckDNS API token (https://www.duckdns.org/)
PROVIDERS_GOOGLE_CLIENT_ID     | Google Oauth client ID (https://console.developers.google.com/apis/credentials)
PROVIDERS_GOOGLE_CLIENT_SECRET | Google Oauth client secret (https://console.developers.google.com/apis/credentials)
SECRET                         | Internal OAuth secret
VPN_USERNAME                   | OpenVPN provider username
VPN_PASSWORD                   | OpenVPN provider password
PLEX_CLAIM                     | Plex claim token needed for first time container setup (https://www.plex.tv/claim/)
JICOFO_COMPONENT_SECRET        | Internal Jitsi secret
JICOFO_AUTH_PASSWORD           | Internal Jitsi password
JVB_AUTH_PASSWORD              | Internal Jitsi password

## Usage

Most services are secured behind Google forward authentication. Plex and Jitsi handle their own authentication to allow for shared usage without whitelisting.

Service           | URL
---               | ---
Traefik Dashboard | https://mchill.duckdns.org
Pi-hole           | https://pihole.mchill.duckdns.org
Portainer         | https://portainer.mchill.duckdns.org
Prometheus        | https://prometheus.mchill.duckdns.org
Jaeger            | https://jaeger.mchill.duckdns.org
Filestash         | https://files.mchill.duckdns.org
qBittorrent       | https://torrent.mchill.duckdns.org
Plex              | https://plex.mchill.duckdns.org
Jitsi             | https://jitsi.mchill.duckdns.org
SFTP              | mchill.duckdns.org:2222
Minecraft         | mchill.duckdns.org:25565
