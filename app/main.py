from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter

from app.v1.dependencies import get_context
from app.v1.graphql.base import Query, Mutation
from app.project.db import init_db
from app.project.settings import settings


schema_v1 = strawberry.Schema(Query, Mutation)

graphql_app_v1 = GraphQLRouter(schema_v1, context_getter=get_context)

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
    await init_db()
