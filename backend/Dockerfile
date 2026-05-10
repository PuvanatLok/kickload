# WHY MULTI-STAGE BUILD:
# Stage 1 (builder) installs dependencies — includes compilers and build tools.
# Stage 2 (runtime) copies only the installed packages — no compilers, smaller image.
# Result: production image is ~200MB instead of ~800MB.
# Smaller image = faster Cloud Run cold starts, lower storage cost.
# ALTERNATIVE: single-stage build — simpler but bloated image, acceptable for dev.

FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt
# --prefix=/install puts packages in a known location for copying.
# --no-cache-dir reduces image layer size.

# ─────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Create non-root user.
# WHY: running as root inside a container means a container escape gives
# an attacker root on the host. Always run app processes as a non-root user.
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app/ ./app/

RUN chown -R app:app /app
USER app

EXPOSE 8000

# Production command — no --reload, workers = 2 * CPU + 1 is standard.
# WHY UVICORN NOT GUNICORN + UVICORN WORKERS:
# Cloud Run scales horizontally (more container instances), not vertically
# (more workers per instance). One uvicorn worker per container is simpler
# and Cloud Run handles the concurrency. Use gunicorn workers only on VMs.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
