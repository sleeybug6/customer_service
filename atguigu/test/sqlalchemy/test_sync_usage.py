"""
sqlalchemy的同步用法
"""

from models import Base, User, Address
from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import Session


def main():
    # 创建引擎
    engine = create_engine(url='mysql+pymysql://root:123456@127.0.0.1:3306/test?charset=utf8mb4', echo=False)

    # # 创建表
    # Base.metadata.create_all(engine)

    # 插入数据
    user1 = User(name='zs1')
    user2 = User(name='ls2')
    user3 = User(name='ww3')
    with Session(engine) as session:

        # session.add_all([user1, user2, user3])

        # session.execute(select(User)).scalars() 等价于session.scalars(select(User)))
        res = session.execute(select(User).where(User.name=='zs1')).scalar() # 查询--->返回结果类型User
        # res = session.execute(select(User).where(User.name.in_(['zs1','ls2']))).scalar() # in

        # res.name = '张三' # 修改数据, commit后就会更新该条数据
        # res = session.execute(select(User).where(User.name.in_(['zs1','ls2']))).scalars() # 返回结果类型ScalarResult,可以用for遍历，每次遍历得到的是User对象; 或者scalars().first()后才是User
        # session.delete(res) # 删除单条数据,commit后就会删除该条数据
        print(res) 
        # 查询多条记录
        for user in session.execute(select(User)).scalars():
        # for user in session.scalars(select(User)): # 与上面等价
            print(user) # user类型为User
        
        session.commit()

    engine.dispose()



if __name__ == "__main__":
    main()


