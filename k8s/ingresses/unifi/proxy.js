const http = require('http');
const https = require('https');

http.createServer((req, res) => {
    const headers = req.headers;
    delete headers['accept-encoding'];

    https.get('https://unifi.server.svc.cluster.local:80/proxy/network/v2/api/site/default/topology', { headers }, (response) => {
        let output = '';
        response.setEncoding('utf8');

        response.on('data', (chunk) => {
            output += chunk;
        });

        response.on('end', () => {
            const data = JSON.parse(output);
            data.vertices.sort((a, b) => {
                const aPort = data.edges.find((edge) => edge.downlinkMac === a.mac)?.uplinkPortNumber || 0;
                const bPort = data.edges.find((edge) => edge.downlinkMac === b.mac)?.uplinkPortNumber || 0;
                return bPort - aPort;
            });

            res.setHeader('Content-Type', 'application/json');
            res.write(JSON.stringify(data));
            res.end();
        });
    });
}).listen(3000);
