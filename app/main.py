from fastapi import FastAPI
import strawberry
from strawberry.fastapi import GraphQLRouter

from app.v1.dependencies import get_context
from app.v1.graphql.base import Query, Mutation
from app.project.db import init_db


schema_v1 = strawberry.Schema(Query, Mutation)

graphql_app_v1 = GraphQLRouter(schema_v1, context_getter=get_context)

app = FastAPI(redoc_url=None, docs_url=None, openapi_url=None)

app.include_router(graphql_app_v1, prefix='/api/v1/users')


@app.on_event('startup')
async def on_startup():
    await init_db()
