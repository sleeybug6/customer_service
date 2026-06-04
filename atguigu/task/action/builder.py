import importlib
import pkgutil
import inspect

from atguigu.task.action.builtin.listener import ActionListener
from atguigu.task.action.builtin.response import ActionResponse
from atguigu.task.action.runner import ActionRunner
from atguigu.task.action.registry import ActionRegistry
from atguigu.task.action.base import Action


def register_builtin_action(action_runner: ActionRunner):
    
    action_listener = ActionListener()
    action_response = ActionResponse()
    action_runner.registry.register(action_listener)
    action_runner.registry.register(action_response)



def register_customer_action(action_runner: ActionRunner):
    '''
    自动扫描自定义action包 完成注册
    '''

    # 获取包信息
    package = importlib.import_module('atguigu.task.action.customer')

    # 遍历package包下的所有模块
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__, prefix=f'{package.__name__}.'):
        
        
        if is_pkg:
            continue
        
        # 导入当前模块
        module = importlib.import_module(module_name)

        # 遍历该模块中的所有类
        for _, cls in inspect.getmembers(module, inspect.isclass):
            
            if not issubclass(cls, Action) or cls is Action:
                continue

            if cls.__module__ != module.__name__:
                continue

            action_runner.registry.register(cls())





def build_action_runner() -> ActionRunner:
    '''获取action_runner'''

    action_runner = ActionRunner(ActionRegistry())

    # 注册action
    register_builtin_action(action_runner)
    register_customer_action(action_runner)



    return action_runner


if __name__ == "__main__":
    
    action_runner = build_action_runner()

    print(action_runner.registry._actions.keys())
