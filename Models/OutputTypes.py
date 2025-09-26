import strawberry

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
    def __init__(self,
                 ing_key,
                 name: str,
                 b_key,
                 amount):
        self.ing_key = ing_key if ing_key is not None else 0
        self.name = name if name is not None else ""
        self.amount = amount if amount is not None else ""
        self.b_key = b_key if b_key is not None else 0

    ing_key: int
    name: str
    b_key: int
    """id should be encode with the custom format: [bi code part].[user/recipe code part].[time stamp derived part]"""
    amount: str  #todo need to find a better way to store and send this data: tuple(int part and str part) or can be just str or int




@strawberry.type
class IngredientContainer:
    def __init__(self,
                 name,
                 ig_list):
        self.name = name
        self.ig_list = ig_list if ig_list is not None else []

    name: str
    ig_list: list[BasicIngredient]


@strawberry.type
class Instructions:
    def __init__(self,
                 order_No,
                 name,
                 step):
        self.order_No = order_No
        self.name = name
        self.step = step

    order_No: int
    name: str
    step: str


@strawberry.type
class InstructionContainer:
    def __init__(self,name, step_list):
        self.name = name if name is not None else ""
        self.step_list = step_list if step_list is not None else []

    name: str
    step_list: list[Instructions]


@strawberry.type
class Collection:
    name: str
    recipe_list: list[RecipeType]


@strawberry.type
class Recipe:
    def __init__(self,
                 name,
                 r_id,
                 description,
                 is_visible,
                 is_owner_match: bool,
                 image_url: str | None,
                 ing_list: list[BasicIngredient] | None,
                 inst_list: list[InstructionContainer] | None,
                 types: list[RecipeType]):
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
    def __init__(self, r_ic: str, name: str, description: str, image_url: str, owner_id: str):
        self.r_ic = r_ic
        self.name = name
        self.description = description
        self.image_url = image_url if image_url is not None else ''
        self.owner_id = owner_id

    r_ic: str
    name: str
    description: str
    image_url: str | None
    owner: str


@strawberry.type
class User:
    u_id: str
    name: str
    profile: str
    own_library: list[Recipe]
    collection_library: list[Collection]
    bookmark_library: list[Recipe]

@strawberry.scalar
def ef():
    pass
