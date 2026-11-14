# Stage 1: compile the static site inside the image (site/ is not in git)
FROM python:3.13-slim AS build
WORKDIR /src
COPY . .
RUN python3 -I scripts/build_short_site.py
# Stage 2: serve it
FROM nginx:1.27-alpine
COPY --from=build /src/site/ /usr/share/nginx/html/
