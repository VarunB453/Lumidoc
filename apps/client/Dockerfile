# =============================================================================
# Lumidoc frontend — multi-stage build, nginx edge.
# =============================================================================

# ---------- Build stage ----------
FROM node:20-alpine AS builder
WORKDIR /app

# Install all deps (including devDependencies like typescript & vite) so the
# build can run. We deliberately do NOT set NODE_ENV=production yet, otherwise
# npm ci would skip devDependencies.
COPY package*.json ./
RUN npm ci --include=dev --no-audit --no-fund

# Anything starting with VITE_ becomes embedded into the bundle at build time.
ENV NODE_ENV=production

COPY . .
# Drop dev-only env files — `vite build` reads .env.production automatically.
RUN rm -f .env .env.development .env.local
RUN npm run build

# ---------- Serve stage ----------
FROM nginx:alpine AS runtime

# Drop the default vhost.
RUN rm -f /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost/ >/dev/null || exit 1

CMD ["nginx", "-g", "daemon off;"]
