import strawberry

import Models


@strawberry.input
class i_Ingredient_List:
    def __init__(self,
                 position_no,
                 name,
                 content):
        self.position_no = position_no if position_no is not None else 0
        self.name = name if name is not None else 'noname'
        self.content_list = content if content is not None else []
    position_no: int
    name: str
    content: list[str] #todo need to figure out what data needs to be in here

@strawberry.input
class i_Instruction_List:
    def __init__(self,
                 position_no,
                 name,
                 content):
        self.position_no = position_no if position_no is not None else 0
        self.name = name if name is not None else 'noname'
        self.content = content if content is not None else []
    position_no: int
    name: str
    content: list[str] #todo need to figure out what data needs to be in here 7


@strawberry.input
class i_Ingredient_Container_List:
    def __init__(self,):
        pass

@strawberry.input
class Search_Term:
    def __inet__(self, R_id,
                 RA_id,
                 RT_id,
                 ):
        pass


@strawberry.input
class Recipe_Query_Payload:
    pass

@strawberry.input
class Payload:
    pass