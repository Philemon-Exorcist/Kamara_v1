import os

from fastapi import HTTPException

LOCAL_CORS_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
)

PRODUCTION_CORS_ORIGINS = (
    "https://kamara.study",
    "https://www.kamara.study",
)


def is_production_environment() -> bool:
    environment = os.getenv("ENVIRONMENT", "").strip().lower()
    return bool(os.getenv("K_SERVICE") or os.getenv("RENDER") or environment in {"prod", "production"})


def is_auth_flow_enabled() -> bool:
    override = os.getenv("ENABLE_AUTH_FLOW")
    if override is not None:
        return override.strip().lower() in {"1", "true", "yes", "on"}

    return not is_production_environment()


def ensure_auth_flow_enabled() -> None:
    if not is_auth_flow_enabled():
        raise HTTPException(status_code=404, detail="Not found.")


def _split_origins(raw_value: str | None) -> list[str]:
    if not raw_value:
        return []

    origins: list[str] = []
    for origin in raw_value.split(","):
        cleaned = origin.strip().rstrip("/")
        if cleaned:
            origins.append(cleaned)
    return origins


def get_cors_allowed_origins() -> list[str]:
    custom_origins = _split_origins(os.getenv("CORS_ALLOWED_ORIGINS"))
    if custom_origins:
        return custom_origins

    if is_production_environment():
        frontend_origin = os.getenv("FRONTEND_APP_URL", "https://kamara.study").rstrip("/")
        origins = {frontend_origin, *PRODUCTION_CORS_ORIGINS}
        return sorted(origins)

    origins = set(LOCAL_CORS_ORIGINS)
    frontend_origin = os.getenv("FRONTEND_APP_URL", "").rstrip("/")
    if frontend_origin:
        origins.add(frontend_origin)
    return sorted(origins)
