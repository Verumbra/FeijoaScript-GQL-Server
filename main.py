from fastapi import FastAPI
import strawberry

from strawberry.fastapi import GraphQLRouter
from mgclient import connect

MG_HOST = "localhost"
MG_PORT = 7687

def get_mgraph_connection():
    return connect(MG_HOST, MG_PORT)




@strawberry.type
class RecipeArchetype:
    RAT_id: str
    name: str
    component_list: list[str]

@strawberry.type
class RecipeType:
    name: str
    RT_id: str

@strawberry.type
class BasicIngredient:
    name: str
    bi_id: str
    """id should be encode with the custom format: [bi code part].[user/recipe code part].[time stamp derived part]"""
    amount: str #todo need to find a better way to store and send this data: tuple(int part and str part) or can be just str or int

@strawberry.type
class IngredientContainer:
    name: str
    ig_list: list[BasicIngredient]

@strawberry.type
class Instructions:
    order_No: int
    step: str

@strawberry.type
class InstructionContainer:
    name: str
    step_list: list[Instructions]



@strawberry.type
class Collection:
    name:str
    recipe_list:list[RecipeType]




@strawberry.type
class Recipe:
    def __init__(self,
                 name,
                 r_id,
                 description,
                 is_visible,
                 is_owner_match:bool,
                 image_url:str | None,
                 ing_list:list[BasicIngredient] | None,
                 inst_list:list[InstructionContainer]| None,
                 types:list[RecipeType]):
        self.name = name
        self.r_id = r_id
        self.description = description
        self.is_visible = is_visible
        self.is_owner_match = is_owner_match
        self.image_url = image_url if image_url is not None else ''
        self.ing_list = ing_list if ing_list is not None else []
        self.inst_list = inst_list if inst_list is not None else []
        self.types = types if types is not None else []

    name: str
    r_id: str
    description: str
    is_visible: bool
    is_owner_matched: bool
    image_url: str
    ingredient_list: list[IngredientContainer]
    instructions: list[InstructionContainer]
    type_list: list[RecipeType]



@strawberry.type
class RPreview:
    def __init__(self,r_ic: str,name: str,description: str,image_url: str,owner_id: str):
        self.r_ic = r_ic
        self.name = name
        self.description = description
        self.image_url = image_url if image_url is not None else ''
        self.owner_id = owner_id
    r_ic: str
    name: str
    description: str
    image_url: str | None
    owner:str


@strawberry.type
class User:
    u_id: str
    name: str
    profile: str
    own_library: list[Recipe]
    collection_library: list[Collection]
    bookmark_library: list[Recipe]

#Query Section


def get_recipe(self,r_id:str) -> Recipe | None:
    with get_mgraph_connection() as mg_connection:
        with mg_connection.cursor() as cursor:
            result = cursor.execute(
                f"""MATCH (r:Recipe {{id: {r_id}}})-[:HAS]->(ic:IngredientContainer)-[:HAS]->(bi:BasicIngredient),
                    (r)-[:HAS]->(incon:InstructionContainer)-[:HAS]->(in:Instructions)
                     WITH
                        r
                        COLLECT(
                        {{
                            name: ic.name,
                            COLLECT({{
                                bid: bi.bi_id,
                                name: bi.name,
                                bkey: bi.key,
                                amount: bi.amount
                            }}) AS baseingredients
                        }}) AS ingredients,
                        COLLECT({{
                            name: incon.name,
                            COLLECT({{
                                orderno: in.orderno
                                body: in.step
                            }}) AS steps
                        }}) AS instructions
                     RETURN {{
                        name: r.name,
                        rid: r.r_id,
                        description: r.description,
                        is_visible: r.is_visible,
                        image_url: r.image_url,
                        ingredients: ingredients,
                        instructions: instructions
                     }} """
            ).fetchall()
            if result:
                pass
    return Recipe()

def get_recipe_from_tuple(recipe_tuple:[tuple])-> [Recipe,int]:
    recipe:Recipe = Recipe(name=recipe_tuple[0],r_id=recipe_tuple[1],description=recipe_tuple[2],is_visible=recipe_tuple[3],is_owner_match=recipe_tuple[4])
    ing_con_list:list[IngredientContainer]
    ing_con_builder:IngredientContainer
    #some logic that extracts







def get_user(self, u_id:str)-> User | None:
    with get_mgraph_connection() as mg_connection:
        user: User
        with mg_connection.cursor() as cursor:

            result = cursor.execute(
                f"""MATCH (u:User {{id: '{u_id}'}}) RETURN u.name, u.profile, u.setting"""
            ).fetchone()
            if result:
                user = User(u_id= u_id, name=result[0], profile=result[1], setting=result[2])
                return user
            else:
                return None

def get_user_library(self, u_id:str)-> list[RPreview]:
    with get_mgraph_connection() as mg_connection:
        library: list[RPreview]
        with mg_connection.cursor() as cursor:
            results = cursor.execute(
                f"""MATCH (u:User {{id: '{u_id}'}})-[:OWN]->(r:Recipe) RETURN r.id,r.name,r.description,r.is_visible"""
            ).fetchall()
            if results:
                for result in results:
                    library.append(RPreview(r_id=result[0],name=result[1],description=result[2],is_visible=result[3]))
                return library
            else: return []

#Mutation Input Section


#Mutation Section

def add_user(self, u_id:str, )-> [str]:
    return ['404','']

def add_recipe(self, u_id:str, )-> [str]:
    return ['404','']

@strawberry.type
class Query:
    #Basic Lookup
    user: User = strawberry.field(resolver=get_user)
    """Use user to get a light wieght version of the user object, the version only has the id, name and profile"""
    library: list[RPreview] = strawberry.field(resolver=get_user_library)
    recipe: Recipe = strawberry.field(resolver=get_recipe)
    #Advance Searches and Metadata lookup

@strawberry.type
class Mutation:
    #Basic Create
    add_user: User = strawberry.mutation(resolver=add_user)
    new_recipe: Recipe = strawberry.mutation(resolver=add_recipe)

    #Update



schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
