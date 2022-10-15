# Production entry point for the frontend docker container

sed -i 's#\[{ src: "~/assets/main.css" }, { src: "~/assets/style-overrides.scss" }\]#[{ src: "~/assets/main.css" }, { src: "~/assets/style-overrides.scss" }, { src: "~/assets/custom.css" }]#' nuxt.config.js
yarn install
yarn build

# Web Server
caddy start --config /app/Caddyfile

# Start Node Application
yarn start -p 3001
