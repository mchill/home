FROM node:12
WORKDIR /app
COPY . .
RUN npm ci
RUN npm run build

FROM nginx
COPY --from=0 /app/build /usr/share/nginx/html
