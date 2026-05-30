# Build stage
FROM node:20-alpine AS build

WORKDIR /app

COPY apps/client/package*.json ./
RUN npm ci

COPY apps/client/ ./
RUN npm run build

# Production stage
FROM nginx:alpine AS production

COPY --from=build /app/dist /usr/share/nginx/html
COPY infrastructure/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
