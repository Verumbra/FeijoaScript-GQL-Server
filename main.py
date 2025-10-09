from fastapi import FastAPI, Depends, Request, HTTPException
import strawberry
from strawberry.types import Info
from psycopg_pool import AsyncConnectionPool

from strawberry.fastapi import GraphQLRouter

from contextlib import asynccontextmanager
import psycopg_pool
import psycopg

from dotenv import load_dotenv
import os

#import Utilty.Synth
import Models.OutputTypes
import Models.InputType

##Memgraph setup section

MG_HOST = "localhost"
MG_PORT = 7687


# async def get_mgraph_connection():
#    return connect(MG_HOST, MG_PORT)


def get_postgres_connection_string():
    return f"""postgresql://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv("PG_HOST")}:{os.getenv('PG_PORT')}"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.async_pool = AsyncConnectionPool(conninfo=get_postgres_connection_string())
    yield
    await app.state.async_pool.close()


# Query Section

# todo need to redo the queries to be parameterized

async def get_recipe(self, r_id: int, info: Info) -> Models.OutputTypes.Recipe | None:
    request = info.context["request"]
    pool: AsyncConnectionPool = app.state.async_pool

    async with pool.connection() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(f"""
            SELECT 
            json_agg(
                json_build_object(
                    'recipe_id',r.id,
                    'recipe_name',r.name,
                    'recipe_Description',r.description,
                    'img_url',r.img_url,
                    'arch_ref',r.recipe_arch_ref_number,
                    'instruction_list',json_agg(
                        json_build_object(
                             "inst_l_id",ins_l.id,
                             'name',ins_l.name,
                             'step', json_agg(
                                json_build_object(
                                        'name',s.name,
                                    'index',s.step_index,
                                    'body',s.step_body
                                )
                             )
                        )
                    ),
                    'ing_list',json_agg(
                        json_build_object(
                            'id',ing_l.id,
                            'name',ing_l.name,
                            'ing', json_agg(
                                json_build_object(
                                    'name',ing.name,
                                    'amount',ing.amount,
                                    'ing_ref',ing.ing_ref_number
                                )
                            )
                        )
                    )
                )
            )
            FROM Recipe r
            LEFT JOIN Instruction_List ins_l ON ins_l.Recipe_ref_number = r.id
            LEFT JOIN Step s ON s.Inst_ref_number = ins_l.id
            LEFT JOIN Ingredient_List ing_l ON ing_l.Recipe_ref_number = r.id
            WHERE r.id = $1

            """, r_id)
            results = await cursor.fetchall()

        if not results:
            raise HTTPException(status_code=404, detail="Recipe not found")

    gu: Models.OutputTypes.Recipe = Utilty.Synth.gen_recipe_from_json(results[0])

    return gu


async def get_ingredient_list(self, r_id, info: Info):
    request = info.context["request"]
    pool: AsyncConnectionPool = app.state.async_pool

    async with pool.connection() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(f"""
            """, r_id)

            results = await cursor.fetchall()

    if not results:
        raise HTTPException(status_code=404, detail="List not found")

    gu = []

    for ingredient in results:
        gu.append(Utilty.Synth.gen_ingredient_list_from_json(ingredient))

    return gu


async def get_user(self, u_id: str, info: Info) -> Models.OutputTypes.User:
    """This resolver is for retrieving user data for a singular user look up. Should not be used for login validation; this function does not bundle in the users library or collections"""
    # todo need to add a profile field to the database table for Customer
    request = info.context["request"]
    pool: AsyncConnectionPool = app.state.async_pool

    async with pool.connection() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(f"""
                SELECT c.username
                FROM Customer
                WHERE user_id = $1
            """, u_id)

            results = await cursor.fetchone()

    if not results:
        raise HTTPException(status_code=404, detail="User not found")

    gu: Models.OutputTypes.User = Utilty.Synth.gen_user_from_json(results[0])

    return gu


async def get_users(self, payload: list[int], info: Info):
    pass


def get_user_library(self, u_id: str) -> list[Models.OutputTypes.RPreview] | None:
    pass


# Mutation Input Section


# Mutation Section

# todo need to make a function that can construct a query with a type indacation and a payload


# create user should be behind a admin protected endpoint and not apart of the normal graph, this is for testing and database seeding and dev
async def add_user(self, u_id: str, name: str, profile: str, info: Info) -> list[str]:
    request = info.context["request"]
    pool: AsyncConnectionPool = app.state.async_pool
    try:
        async with pool.connection() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"""
                """, u_id, name, profile)

    except Exception as e:
        print(e)
        return ["400 Bad Request"]
    return ["202 Accepted"]


async def add_recipe(self, u_id: str, r_name: str, r_description: str,
                     inst_con: list[Models.InputType.i_Instruction_List],
                     ing_con: list[Models.InputType.i_Ingredient_List], info: Info) -> str:
    request = info.context["request"]
    pool: AsyncConnectionPool = app.state.async_pool

    try:
        async with pool.connection() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"""
                """, u_id, r_name, r_description, inst_con, ing_con)

    except Exception as e:

        print(e)
        return '404 bad command'
    return '202 status ok'


def set_ingredients(self, u_id: str, ingredient_list: list[Models.OutputTypes.BasicIngredient]) -> str:
    pass


@strawberry.type
class Query:
    # Basic Lookup
    user: Models.OutputTypes.User = strawberry.field(resolver=get_user)
    """Use user to get a light weight version of the user object, the version only has the id, name and profile"""
    library: list[Models.OutputTypes.RPreview] = strawberry.field(
        resolver=get_user_library)  # the defualt value that should be return is a list of RPreviews but that will cause an error if typed that way on this line
    recipe: Models.OutputTypes.Recipe = strawberry.field(resolver=get_recipe)

    # Advance Searches and Metadata lookup


@strawberry.type
class Mutation:
    # Basic Create
    add_user: Models.OutputTypes.User = strawberry.mutation(resolver=add_user)
    new_recipe: Models.OutputTypes.Recipe = strawberry.mutation(resolver=add_recipe)

    # Update


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI(lifespan=lifespan)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# repository