import asyncio
import logging

import sentry_sdk
import strawberry
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.project.rmq import connection
from app.project.settings import settings
from app.v1.dependencies import get_context
from app.v1.graphql.base import Mutation, Query
from app.v1.grpc import start_server

logger = logging.getLogger("uvicorn.error")

logger.debug(f"Initing sentry for dsn: {settings.sentry_link}. Environment: {settings.run_mode}")
if settings.sentry_link:
    sentry_sdk.init(settings.sentry_link, environment=settings.run_mode)

schema_v1 = strawberry.Schema(Query, Mutation)

graphql_app_v1 = GraphQLRouter(
    schema_v1,
    context_getter=get_context,
    graphiql=False if settings.run_mode == 'prod' else True,
)

app = FastAPI(redoc_url=None, docs_url=None, openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(graphql_app_v1, prefix='/api/v1/users')


@app.on_event('startup')
async def on_startup():
    loop = asyncio.get_running_loop()
    asyncio.run_coroutine_threadsafe(start_server(), loop)
    await connection.connect()
