FROM nginx:alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY infrastructure/nginx/nginx.conf /etc/nginx/nginx.conf
COPY infrastructure/nginx/conf.d/ /etc/nginx/conf.d/
COPY infrastructure/nginx/snippets/ /etc/nginx/snippets/

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
