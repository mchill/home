import React, { useState } from 'react';
import {
    AppBar, Card, CardActionArea, CardContent, CardMedia, Divider, IconButton, List,
    ListItem, ListItemIcon, ListItemText, SwipeableDrawer, Toolbar, Typography
} from '@material-ui/core';
import { ChevronLeft, ExitToApp, Menu } from '@material-ui/icons';
import styled from 'styled-components';

import bazarr from './logos/bazarr.png';
import filebrowser from './logos/filebrowser.png';
import grafana from './logos/grafana.png';
import homeassistant from './logos/homeassistant.png';
import jackett from './logos/jackett.png';
import jitsi from './logos/jitsi.png';
import kubernetes from './logos/kubernetes.png';
import nas from './logos/nas.png';
import pihole from './logos/pihole.png';
import plex from './logos/plex.png';
import prometheus from './logos/prometheus.png';
import radarr from './logos/radarr.png';
import sonarr from './logos/sonarr.png';
import traefik from './logos/traefik.png';
import transmission from './logos/transmission.png';

const DrawerHeader = styled.div`
    display: flex;
    justify-content: flex-end;
    width: 250px;
    height: 64px;
`;

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
    { name: "Bazarr", subdomain: "bazarr", logo: bazarr },
    { name: "File Browser", subdomain: "files", logo: filebrowser },
    { name: "Grafana", subdomain: "grafana", logo: grafana },
    { name: "Home Assistant", subdomain: "home", logo: homeassistant },
    { name: "Jackett", subdomain: "jackett", logo: jackett },
    { name: "Jitsi", subdomain: "jitsi", logo: jitsi },
    { name: "K8s Dashboard", subdomain: "k8s", logo: kubernetes },
    { name: "NAS", subdomain: "nas", logo: nas },
    { name: "Pi-hole", subdomain: "pihole", logo: pihole },
    { name: "Plex", subdomain: "plex", logo: plex, path: "/web/index.html" },
    { name: "Prometheus", subdomain: "prometheus", logo: prometheus },
    { name: "Radarr", subdomain: "radarr", logo: radarr },
    { name: "Sonarr", subdomain: "sonarr", logo: sonarr },
    { name: "Traefik", subdomain: "traefik", logo: traefik },
    { name: "Transmission", subdomain: "transmission", logo: transmission }
];

function App() {
    const [drawer, setDrawer] = useState(false);

    return (
        <>
            <AppBar position="sticky" color="primary">
                <Toolbar>
                    <IconButton edge="start" color="inherit" aria-label="menu" onClick={() => setDrawer(true)}>
                        <Menu />
                    </IconButton>
                    <Typography variant="h6" color="inherit">
                        Home Server
                    </Typography>
                </Toolbar>
            </AppBar>
            <SwipeableDrawer
                variant="temporary"
                anchor="left"
                open={drawer}
                onOpen={() => setDrawer(true)}
                onClose={() => setDrawer(false)}
                ModalProps={{
                    keepMounted: true,
                }}
            >
                <DrawerHeader>
                    <IconButton onClick={() => setDrawer(false)}>
                        <ChevronLeft />
                    </IconButton>
                </DrawerHeader>
                <Divider />
                <List>
                    <ListItem button component="a" href="https://auth.mchill.duckdns.org/_oauth/logout">
                        <ListItemIcon>
                            <ExitToApp />
                        </ListItemIcon>
                        <ListItemText primary="Logout" />
                    </ListItem>
                </List>
            </SwipeableDrawer>
            <AppList>
                {apps.map((app) => (
                <AppCard key={app.name}>
                    <AppAction onClick={() => window.location.assign("https://" + app.subdomain + ".mchill.duckdns.org" + (app.path || ""))}>
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
