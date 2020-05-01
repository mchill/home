import React from 'react';
import {
    AppBar, Card, CardActionArea, CardContent, CardMedia, IconButton,
    Toolbar, Typography
} from '@material-ui/core';
import { Menu } from '@material-ui/icons';
import styled from 'styled-components';

import filestash from './logos/filestash.png';
import grafana from './logos/grafana.png';
import jaeger from './logos/jaeger.png';
import jitsi from './logos/jitsi.png';
import pihole from './logos/pihole.png';
import plex from './logos/plex.png';
import portainer from './logos/portainer.png';
import prometheus from './logos/prometheus.png';
import qbittorrent from './logos/qbittorrent.svg';
import traefik from './logos/traefik.png';

const AppList = styled.div`
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    margin: auto;
    margin-top: 50px;
    max-width: 800px;
`;

const AppCard = styled(Card)`
    display: flex;
    background-color: ghostwhite;
    box-shadow: none;
    min-width: 150px;
    height: 150px;
    transform: all 0.2s ease-in-out;
    &:hover {
        transform: scale(1.1);
    }
`;

const AppAction = styled(CardActionArea)`
    display: flex;
    flex-direction: column;
    align-items: stretch;
`;

const AppImage = styled(CardMedia)`
    flex-grow: 1;
    width: 100%;
    background-size: contain;
`;

const AppName = styled(Typography)`
    color: darkslategrey;
`;

const apps = [
    { name: "Filestash", subdomain: "files", logo: filestash },
    { name: "Grafana", subdomain: "grafana", logo: grafana },
    { name: "Jaeger", subdomain: "jaeger", logo: jaeger },
    { name: "Jitsi", subdomain: "jitsi", logo: jitsi },
    { name: "Pi-hole", subdomain: "pihole", logo: pihole },
    { name: "Plex", subdomain: "plex", logo: plex },
    { name: "Portainer", subdomain: "portainer", logo: portainer },
    { name: "Prometheus", subdomain: "prometheus", logo: prometheus },
    { name: "qBittorrent", subdomain: "torrent", logo: qbittorrent },
    { name: "Traefik", subdomain: "traefik", logo: traefik }
];

function App() {
    return (
        <>
            <AppBar position="sticky" color="primary">
                <Toolbar>
                    <IconButton edge="start" color="inherit" aria-label="menu">
                    <Menu />
                    </IconButton>
                    <Typography variant="h6" color="inherit">
                        Home Server
                    </Typography>
                </Toolbar>
            </AppBar>
            <AppList>
                {apps.map((app) => (
                <AppCard color={app.color}>
                    <AppAction onClick={() => window.location.assign("https://" + app.subdomain + ".mchill.duckdns.org")}>
                        <AppImage image={app.logo} />
                        <CardContent>
                            <AppName variant="body1" align="center">
                                {app.name}
                            </AppName>
                        </CardContent>
                    </AppAction>
                </AppCard>
                ))}
            </AppList>
        </>
    );
}

export default App;
