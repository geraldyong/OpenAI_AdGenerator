FROM python:3.12-slim

# Create app user.
# Use this for non-alpine.
#RUN useradd --user-group --system --no-log-init --create-home appusr
# Use this for alpine.
RUN addgroup --system apps --gid 1000 && adduser --system appuser --uid 1000 --gid 1000

# Copy files.
WORKDIR /app
COPY --chown=appuser:apps *.py  /app
COPY --chown=appuser:apps *.txt /app
COPY --chown=appuser:apps certs /app/certs

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir "uvicorn[standard]" && \
    rm -f /app/requirements.txt

USER appuser

EXPOSE 8000

CMD ["uvicorn", "adgen_ms:app", "--host", "0.0.0.0", "--reload", "--ssl-keyfile", "certs/geraldyong-priv.pem", "--ssl-certfile", "certs/geraldyong-cert.pem"]
