# Home Server

This is the configuration for my home server.

![Home Server](https://github.com/mchill/home/workflows/Home%20Server/badge.svg)

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
22         | 22        | SSH
25565      | 25565     | Minecraft
25566      | 25566     | Minecraft
4443       | 4443      | Jitsi
10000/udp  | 10000/udp | Jitsi

### Filesystem

The filesystem is split into three parts: version controlled configuration, persisted server data, and large media (for Plex library and torrents). The root paths are configured in .env as REPO_PATH, SERVER_PATH, and DATA_PATH.

SERVER_PATH and DATA_PATH are backed up daily to both local and cloud storage.

### Environment

Set the following environment variables.

Variable                            | Description
---                                 | ---
DUCKDNS_TOKEN                       | DuckDNS API token (https://www.duckdns.org/)
GF_SMTP_PASSWORD                    | Google app password (https://myaccount.google.com/apppasswords)
JICOFO_AUTH_PASSWORD                | Jitsi password
JICOFO_COMPONENT_SECRET             | Jitsi secret
JVB_AUTH_PASSWORD                   | Jitsi password
OAUTH_SECRET                        | OAuth secret
PLEX_CLAIM                          | Plex claim token needed for first time container setup (https://www.plex.tv/claim/)
PROVIDERS_GOOGLE_CLIENT_ID          | Google Oauth client ID (https://console.developers.google.com/apis/credentials)
PROVIDERS_GOOGLE_CLIENT_SECRET      | Google Oauth client secret (https://console.developers.google.com/apis/credentials)
VPN_USERNAME                        | OpenVPN provider username
VPN_PASSWORD                        | OpenVPN provider password

## Usage

Most services are secured behind Google forward authentication. Some services handle their own authentication to allow for shared usage without whitelisting.

Service              | URL
---                  | ---
Dashboard            | https://mchill.duckdns.org
cAdvisor             | https://cadvisor.mchill.duckdns.org
File Browser         | https://files.mchill.duckdns.org
Grafana              | https://grafana.mchill.duckdns.org
Home Assistant       | https://home.mchill.duckdns.org
Jaeger               | https://jaeger.mchill.duckdns.org
Jitsi                | https://jitsi.mchill.duckdns.org
Minecraft            | mchill.duckdns.org:25565
Minecraft (Hogwarts) | mchill.duckdns.org:25566
Pi-hole              | https://pihole.mchill.duckdns.org
Plex                 | https://plex.mchill.duckdns.org
Portainer            | https://portainer.mchill.duckdns.org
Prometheus           | https://prometheus.mchill.duckdns.org
SSH                  | mchill.duckdns.org:22
Synology DSM         | https://nas.mchill.duckdns.org
Traefik Dashboard    | https://traefik.mchill.duckdns.org
qBittorrent          | https://torrent.mchill.duckdns.org
