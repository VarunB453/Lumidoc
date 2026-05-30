# nginx (legacy)

The reverse proxy lives inside the **frontend** container — see
`../../apps/client/nginx.conf`. The frontend image serves the SPA AND proxies
`/api/`, `/local-files/`, and the SSE chat-stream endpoint to the backend on
the docker network.

This directory is kept around in case you want to run a separate edge
(e.g. behind a CDN or with TLS termination at a managed load-balancer). The
old standalone `nginx.conf` was removed to avoid two competing nginx layers.
