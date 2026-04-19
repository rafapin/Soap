from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api.routes import alarms, health, metrics
from app.core.config import settings
from app.core.exceptions import AlarmNotFoundError, IngestionError, ScadaBaseError
from app.core.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="SCADA Alarm Gateway API",
    description=(
        "REST API for querying, filtering and aggregating SCADA alarm data. "
        "Includes a full ETL pipeline for ingesting CSV/JSON alarm datasets."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router)
app.include_router(alarms.router)
app.include_router(metrics.router)


def _validation_details(errors: list[dict]) -> list[str]:
    return [f"{' -> '.join(str(l) for l in error['loc'])}: {error['msg']}" for error in errors]


@app.exception_handler(AlarmNotFoundError)
async def alarm_not_found_handler(request: Request, exc: AlarmNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": "not_found", "message": exc.message, "details": exc.details},
    )


@app.exception_handler(ScadaBaseError)
async def scada_base_error_handler(request: Request, exc: ScadaBaseError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"error": "domain_error", "message": exc.message, "details": exc.details},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Request validation failed",
            "details": _validation_details(exc.errors()),
        },
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Request validation failed",
            "details": _validation_details(exc.errors()),
        },
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "details": [],
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.api_host, port=settings.api_port, reload=settings.debug)
