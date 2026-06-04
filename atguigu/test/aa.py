# import  sqlalchemy
# print(sqlalchemy.__version__)

from dataclasses import dataclass,asdict
from typing import TypedDict

@dataclass
class Obj:
    s:str

@dataclass
class Te:

    a:int
    b:int
    obj:Obj


    def to_dict(self):
        return {
            'a':self.a,
            'b':self.b,
        }






o1 = Obj(s='123')
t1 = Te(a=1,b=2,obj=o1)


# t2 = Te(a=2,b=4)
