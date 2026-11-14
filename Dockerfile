# Stage 1: compile the static site inside the image (site/ is not in git)
FROM python:3.13-slim AS build
WORKDIR /src
COPY . .
RUN python3 -I scripts/build_short_site.py

# Stage 2: ONE process serves the API and the site (uvicorn). The database lives on the Fly volume at /data.
FROM python:3.13-slim
WORKDIR /app
COPY api/requirements.txt api/requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt
COPY --from=build /src/api api
COPY --from=build /src/site site
COPY --from=build /src/assets/terms assets/terms
ENV D2_DB=/data/terms.db D2_SITE=/app/site D2_SEED=/app/assets/terms PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers", "--forwarded-allow-ips", "*"]
