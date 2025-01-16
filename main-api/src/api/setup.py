import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .common.jwt import JWTService
from .config import (
    APIConfig,
    CORSSettings,
    JWTSettings,
    IssueTrackerSettings
)
from . import api
from .dependencies import setup_dependencies
from .rewards.issue_tracker import IssueTrackerService


def setup_middlewares(app: FastAPI, cors_settings: CORSSettings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_settings.allow_origins,
        allow_credentials=cors_settings.allow_credentials,
        allow_methods=cors_settings.allow_methods,
        allow_headers=cors_settings.allow_headers
    )


def setup_services(jwt_settings: JWTSettings, issue_tracker_settings: IssueTrackerSettings) -> None:
    JWTService.setup(
        algorithm=jwt_settings.algorithm,
        access_token_secret=jwt_settings.access_token_secret,
    )
    IssueTrackerService.setup(
        secret=issue_tracker_settings.secret
    )


def get_fastapi_app(config: APIConfig) -> FastAPI:
    app = FastAPI(
        title=config.title,
        version=config.version if config.version else "0.0.0",

        docs_url="/api/docs" if config.enable_docs else None,
        openapi_url="/api/openapi.json" if config.enable_docs else None
    )

    setup_middlewares(app, config.cors_settings)
    setup_services(config.jwt_settings, config.issue_tracker_settings)
    setup_dependencies(app)

    app.include_router(api.router, prefix="/api")

    return app


def get_uvicorn_log_config():
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(asctime)s %(levelprefix)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO"},
            "uvicorn.error": {"handlers": ["default"], "level": "INFO"},
            "uvicorn.access": {"handlers": ["default"], "level": "INFO", "propagate": False},
        },
    }

    return log_config



async def run_api(
    host: str,
    port: int,
    config: APIConfig
) -> None:
    uvicorn_config = uvicorn.Config(
        app=get_fastapi_app(config),
        host=host,
        port=port,
        log_config=get_uvicorn_log_config()
    )
    uvicorn_server = uvicorn.Server(uvicorn_config)
    await uvicorn_server.serve()
