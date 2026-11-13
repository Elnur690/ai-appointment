FROM node:20-alpine AS base

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# --- Development target (used by docker-compose.dev.yml) ---
FROM base AS development
EXPOSE 22300
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "22300"]

# --- Build static production bundle ---
FROM base AS builder
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# --- Production target (default for docker compose up -d) ---
FROM nginx:1.27-alpine AS production

COPY --from=builder /app/dist /usr/share/nginx/html

RUN printf 'server {\n\
    listen 22300;\n\
    server_name _;\n\
    server_tokens off;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    gzip on;\n\
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml image/svg+xml;\n\
    add_header X-Content-Type-Options "nosniff" always;\n\
    add_header X-Frame-Options "SAMEORIGIN" always;\n\
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;\n\
    location /api/ {\n\
        resolver 127.0.0.11 valid=30s ipv6=off;\n\
        set $backend_upstream http://backend:22800;\n\
        proxy_pass $backend_upstream;\n\
        proxy_http_version 1.1;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
        proxy_set_header X-Forwarded-Proto $scheme;\n\
    }\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 22300

CMD ["nginx", "-g", "daemon off;"]
