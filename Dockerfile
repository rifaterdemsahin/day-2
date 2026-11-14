# Static site (built by scripts/build_short_site.py into site/) served by nginx
FROM nginx:1.27-alpine
COPY site/ /usr/share/nginx/html/
