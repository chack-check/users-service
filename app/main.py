from fastapi import FastAPI
import strawberry
from strawberry.fastapi import GraphQLRouter

from app.v1.graphql import Query, Mutation
from app.project.db import engine, Base


schema_v1 = strawberry.Schema(Query, Mutation)

graphql_app_v1 = GraphQLRouter(schema_v1)

app = FastAPI(redoc_url=None, docs_url=None, openapi_url=None)

app.include_router(graphql_app_v1, prefix='/api/v1/users')


@app.on_event('startup')
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
