# syntax=docker/dockerfile:1
FROM golang:1.25-alpine AS api-builder
ARG GIT_COMMIT
ENV GIT_COMMIT=$GIT_COMMIT
WORKDIR /http-sms
COPY api/go.mod api/go.sum ./
RUN go mod download
COPY api/ ./
RUN CGO_ENABLED=0 go build -ldflags "-X main.Version=$GIT_COMMIT" -o /bin/http-sms .

FROM node:22-alpine AS web-builder
WORKDIR /app
COPY web/package.json web/pnpm-lock.yaml ./
RUN npm install -g pnpm@9 && HUSKY=0 pnpm install
COPY web/ ./
RUN ./node_modules/.bin/nuxt generate

FROM alpine:3.20
RUN apk add --no-cache curl nginx supervisor
COPY --from=api-builder /bin/http-sms /usr/local/bin/
COPY --from=api-builder /http-sms/root.crt /etc/ssl/certs/
COPY --from=web-builder /app/.output/public /usr/share/nginx/html
RUN mkdir -p /run/nginx /etc/nginx/http.d && \
echo 'server { listen 3000; server_name localhost; root /usr/share/nginx/html; index index.html index.htm; location / { try_files $uri $uri/ /index.html; } location /api/ { proxy_pass http://127.0.0.1:8000/; proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr; proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; proxy_set_header X-Forwarded-Proto $scheme; } }' > /etc/nginx/http.d/default.conf
RUN echo '[supervisord]\nnodaemon=true\n\n[program:api]\ncommand=http-sms --dotenv=false\nautorestart=true\nstdout_logfile=/dev/stdout\nstdout_logfile_maxbytes=0\nstderr_logfile=/dev/stderr\nstderr_logfile_maxbytes=0\n\n[program:web]\ncommand=nginx -g "daemon off;"\nautorestart=true\nstdout_logfile=/dev/stdout\nstdout_logfile_maxbytes=0\nstderr_logfile=/dev/stderr\nstderr_logfile_maxbytes=0' > /etc/supervisord.conf
ENV ENV=local GOTRACEBACK=all
COPY --from=api-builder /usr/local/go/lib/time/zoneinfo.zip /
EXPOSE 3000 8000
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
