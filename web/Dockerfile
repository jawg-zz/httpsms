# build stage
FROM node:22-alpine AS build

WORKDIR /app

COPY package.json pnpm-lock.yaml ./

# Install pnpm v9 (avoids pnpm v10 build-approval system)
RUN npm install -g pnpm@9 && HUSKY=0 pnpm install

COPY . .
COPY .env.production .env

# Debug: check files exist
RUN ls -la package.json && cat package.json | head -5

# Use explicit npx path for nuxt generate
RUN ./node_modules/.bin/nuxt generate

# production stage
FROM nginx:stable-alpine AS production
COPY --from=build /app/.output/public /usr/share/nginx/html

# Copy the nginx configuration file
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
