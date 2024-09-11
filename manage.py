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
        with database.MongoDBConnectionManager() as _:
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


@click.command("runserver")
def run_server():
    uvicorn.run(
        settings.UVICORN_NAME,
        host=settings.UVICORN_HOST,
        port=settings.UVICORN_PORT,
        reload=settings.UVICORN_RELOAD
    )


@click.command()
def migrate():
    with database.MongoDBConnectionManager() as _:
        asyncio.run(database.Migration.commit())


# RUN THIS COMMAND AFTER MIGRATING TO PREVENT DuplicateKeyError.
@click.command("createsuperuser")
def create_super_user():
    asyncio.run(database.MongoDBConnectionManager.create_super_user())


cli.add_command(run_server)
cli.add_command(migrate)
cli.add_command(create_super_user)


if __name__ == "__main__":
    cli()
