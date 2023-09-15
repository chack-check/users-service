import asyncio

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter

from app.v1.dependencies import get_context
from app.v1.graphql.base import Query, Mutation
from app.v1.grpc import start_server
from app.project.settings import settings


if settings.sentry_link:
    sentry_sdk.init(settings.sentry_link)

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
