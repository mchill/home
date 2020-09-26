import React from 'react';
import {
    AppBar, Card, CardActionArea, CardContent, CardMedia, IconButton,
    Toolbar, Typography
} from '@material-ui/core';
import { Menu } from '@material-ui/icons';
import styled from 'styled-components';

import cadvisor from './logos/cadvisor.png';
import filestash from './logos/filestash.png';
import grafana from './logos/grafana.png';
import jaeger from './logos/jaeger.png';
import jitsi from './logos/jitsi.png';
import nas from './logos/nas.png';
import pihole from './logos/pihole.png';
import plex from './logos/plex.png';
import portainer from './logos/portainer.png';
import prometheus from './logos/prometheus.png';
import qbittorrent from './logos/qbittorrent.svg';
import traefik from './logos/traefik.png';

const AppList = styled.div`
    display: flex;
    flex-wrap: wrap;
    width: 100%;
    margin: auto;
    margin-top: 25px;
    @media (min-width:330px) {
        width: 330px;
    }
    @media (min-width:495px) {
        width: 495px;
    }
    @media (min-width:660px) {
        width: 660px;
    }
`;

const AppCard = styled(Card)`
    display: flex;
    background-color: whitesmoke;
    box-shadow: none;
    min-width: 150px;
    height: 150px;
    margin-bottom: 15px;
    margin-right: 15px;
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
    margin-top: 15px;
    background-size: contain;
`;

const AppName = styled(Typography)`
    color: darkslategrey;
`;

const apps = [
    { name: "cAdvisor", subdomain: "cadvisor", logo: cadvisor },
    { name: "Filestash", subdomain: "files", logo: filestash },
    { name: "Grafana", subdomain: "grafana", logo: grafana },
    { name: "Jaeger", subdomain: "jaeger", logo: jaeger },
    { name: "Jitsi", subdomain: "jitsi", logo: jitsi },
    { name: "NAS", subdomain: "nas", logo: nas },
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
                <AppCard key={app.name}>
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
