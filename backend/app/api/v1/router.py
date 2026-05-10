from fastapi import APIRouter

from app.api.v1 import matches, stadiums

# WHY API VERSIONING (/v1/):
# Once an API is live and clients (the Flutter app) depend on it, you cannot
# change a response shape without breaking those clients. /v1/ lets you build
# /v2/ with breaking changes while /v1/ stays alive for old app versions.
# Mobile apps update slowly — some users stay on old versions for months.
# ALTERNATIVE: header-based versioning (Accept: application/vnd.api+json;version=1)
# — more HTTP-correct but harder to test and document. URL versioning is simpler.

router = APIRouter(prefix="/v1")
router.include_router(matches.router)
router.include_router(stadiums.router)
