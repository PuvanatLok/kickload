from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router
from app.config import settings

app = FastAPI(
    title="KickLoad API",
    version="0.1.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url=None,
    # WHY DISABLE DOCS IN PRODUCTION:
    # /docs exposes your full API surface to anyone who finds the URL.
    # Internal teams use staging for API exploration. Production docs = attack surface.
    # FUTURE: protect /docs with IP allowlist or basic auth rather than disabling.
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not settings.is_production else ["https://kickload.app"],
    allow_methods=["*"],
    allow_headers=["*"],
    # Wide-open CORS in dev so Flutter web and Postman work without friction.
    # Locked to the production domain in prod.
)

app.include_router(router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.env}
    # WHY A HEALTH ENDPOINT:
    # Cloud Run, load balancers, and monitoring tools ping /health to verify
    # the service is alive. Without it, they fall back to pinging / which
    # might return a 404 and incorrectly mark the service as down.
