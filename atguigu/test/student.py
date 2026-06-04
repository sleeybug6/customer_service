

class Person:
    def __init__(self, name, age, d={}):
        
        self.name = name
        self.age = age
        self.d = d

    @classmethod    
    def wt(cls, name, age):
        return cls(name,age)


class Student(Person):
    def __init__(self, name, age, d={}):
        super().__init__(name, age, d)
        self.ll = 123
    


from dataclasses import dataclass

from typing import TypedDict
class Test(TypedDict):
    name:str
    age:str


d = {'name':'zs', 'age':'18', 'gender':'male'}
t1 = Test(**d)
print(t1)



# a = Student.wt('ww',22)
# print(a)


