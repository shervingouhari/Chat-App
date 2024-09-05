from contextlib import asynccontextmanager
from importlib import import_module
import asyncio

from fastapi import FastAPI, Request, responses
import uvicorn
import click

from core import settings, database, exceptions


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        with database.ConnectionManager() as _:
            yield

    app = FastAPI(
        lifespan=lifespan,
        title=settings.FAST_API_TITLE,
        version=settings.FAST_API_VERSION,
        debug=settings.FAST_API_DEBUG,
    )

    @app.exception_handler(500)
    async def internal_server_error_handler(request: Request, exc: Exception):
        error = exceptions.ChatAppAPIError()
        return responses.JSONResponse(
            status_code=error.status_code,
            content={"detail": error.detail}
        )

    for directory in settings.ROUTER_DIRS:
        router = import_module(f"{directory}.router")
        app.include_router(
            router.router,
            prefix=f"/{settings.API_PREFIX}/{directory}",
            tags=[directory]
        )

    return app


app = create_app()


@click.group()
def cli():
    pass


@click.command()
def runserver():
    uvicorn.run(
        settings.UVICORN_NAME,
        host=settings.UVICORN_HOST,
        port=settings.UVICORN_PORT,
        reload=settings.UVICORN_RELOAD
    )


@click.command()
def migrate():
    with database.ConnectionManager() as _:
        asyncio.run(database.Migration.commit())


cli.add_command(runserver)
cli.add_command(migrate)


if __name__ == "__main__":
    cli()
