from pathlib import Path

from atguigu.clarifyer.responser import ClarifyResponser
from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.plan.planner import TurnPlanner
from atguigu.plan.validator import TurnValidator
from atguigu.task.action.runner import ActionRunner
from atguigu.task.command.processor import CommandProcessor
from atguigu.task.flow.executor import FlowExecutor
from atguigu.task.handler import TaskHandler
from atguigu.task.flow.loader import FlowLoader
from atguigu.knowledge.handler import KnowledgeHandler
from atguigu.chitchat.handler import ChitchatHandler
from atguigu.chitchat.responser import ChitchatResponser

from atguigu.knowledge.intents import KNOWLEDGE_INTENTS
from atguigu.knowledge.registry import KnowledgeProviderRegistry
from atguigu.knowledge.providers import OrderAPIProvider, ProductAPIProvider, RAGProvider, FAQProvider
from atguigu.knowledge.responser import KnowledgeResponser

from atguigu.task.action.builder import build_action_runner

# 真正加载YAML
PROJECT_DIR = Path(__file__).resolve().parents[2]
FLOW_CONFIG = PROJECT_DIR / 'flow_config'
flow_config_files = ['user_flows.yml', 'system_flows.yml']

def build_dialogue_engine():
    flows = FlowLoader().load_many([FLOW_CONFIG/file_name for file_name in flow_config_files])
    


    return DialogueEngine(
        turn_planner=TurnPlanner(),
        turn_validator=TurnValidator(),
        clarify_responser=ClarifyResponser(),
        task_handler=TaskHandler(flows=flows, command_processor=CommandProcessor(), action_runner=build_action_runner(), flow_executor=FlowExecutor()),
        knowledge_handler=KnowledgeHandler(knowledge_intents=KNOWLEDGE_INTENTS, provider_registry=KnowledgeProviderRegistry([OrderAPIProvider(), ProductAPIProvider(), RAGProvider(), FAQProvider()]), responser=KnowledgeResponser()),
        chitchat_handler=ChitchatHandler(responser=ChitchatResponser()),
        
    )


