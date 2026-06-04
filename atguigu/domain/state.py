import time
import uuid
from typing import Dict, Any
from dataclasses import dataclass,field
from atguigu.domain.messages import UserMessage, BotMessage, FocusedObject
from atguigu.domain.contexts import TaskContext, SystemContext

@dataclass
class Turn:
    '''
    本轮对话的对象
    '''
    turn_id:str
    user_message:UserMessage
    bot_messages:list[BotMessage]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'turn_id':self.turn_id,
            'user_message':self.user_message.to_dict(),
            'bot_messages':[bot_message.to_dict() for bot_message in self.bot_messages]
        }
    
    @classmethod
    def from_dict(cls, data:Dict[str, Any]) -> 'Turn':
        return cls(
            turn_id=data['turn_id'],
            user_message=UserMessage.from_dict(data['user_message']),
            bot_messages=[BotMessage.from_dict(bot_message_dict) for bot_message_dict in data['bot_messages']]
        )

@dataclass(slots=True)
class Session:
    session_id:str
    started_at:float
    last_activity_at:float # 该会话最后一次活跃时间，用于判断超时
    closed_at:float | None = None # session是否关闭了，如果关闭就会有具体关闭的float数据
    turns:list[Turn] = field(default_factory=list) # 当前对话的多轮

    def to_dict(self) -> Dict[str, Any]:
        return {
            'session_id':self.session_id,
            'started_at':self.started_at,
            'last_activity_at':self.last_activity_at,
            'closed_at':self.last_activity_at,
            'turns':[turn.to_dict() for turn in self.turns]
        }

    @classmethod
    def from_dict(cls, data:Dict[str,Any]) -> 'Session':
        return cls(
            session_id=data['session_id'],
            started_at=data['started_at'],
            last_activity_at=data['last_activity_at'],
            closed_at=data.get('closed_at'),
            turns=[Turn.from_dict(turn_dict) for turn_dict in data.get('turns',[])]
        )

@dataclass(slots=True)
class DialogueState:
    sender_id:str # 必须传入
    active_task:TaskContext | None = None # 当前执行的业务任务
    paused_tasks:list[TaskContext] = field(default_factory=list) # 当前暂停的业务任务(多个)
    active_system_task:SystemContext | None = None # 当前激活的系统流程
    focused_object:FocusedObject | None = None 
    sessions:list[Session] = field(default_factory=list) # 当前用户的所有会话都存储起来
    current_session_id:str | None = None  # 当前用户的当前会话ID
    pending_turn:Turn | None = None # turn会话暂存区(变量:内存中的缓冲区)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sender_id':self.sender_id,
            'active_task':self.active_task.to_dict() if self.active_task else None,
            'paused_tasks':[paused_task.to_dict() for paused_task in self.paused_tasks],
            'active_system_task':self.active_system_task.to_dict() if self.active_system_task else None,
            'focused_object':self.focused_object.to_dict() if self.focused_object else None,
            'sessions':[session.to_dict() for session in self.sessions],
            'current_session_id':self.current_session_id,
            # 'pending_turn':self.pending_turn.to_dict() if self.pending_turn else None
        }

    @classmethod
    def from_dict(cls, data:Dict[str, Any]) -> 'DialogueState':
        return cls(
            sender_id=data['sender_id'],
            active_task= TaskContext.from_dict(data['active_task']) if data.get('active_task') else None,
            paused_tasks = [TaskContext.from_dict(paused_task_dict) for paused_task_dict in data.get('paused_tasks',[])],
            active_system_task=SystemContext.from_dict(data['active_system_task']) if data.get('active_system_task') else None,
            focused_object=FocusedObject.from_dict(data['focused_object']) if data.get('focused_object') else None,
            sessions = [Session.from_dict(session_dict) for session_dict in data.get('sessions', [])],
            current_session_id=data.get('current_session_id'),
            pending_turn=Turn.from_dict(data['pending_turn']) if data.get('pending_turn') else None
        )
    
    # --------------任务相关--------------------------
    def start_active_system_task(self, active_system_task:SystemContext):
        """
        开启系统流程
        Args:
            active_system_task (SystemContext): _description_
        """
        self.active_system_task = active_system_task
    
    def end_active_system_task(self):
        """
        结束系统流程
        """
        self.active_system_task = None
    
    def start_active_task(self, active_task:TaskContext):
        """
        开始业务任务


        Args:
            active_task (TaskContext): _description_
        """
        self.active_task = active_task
    
    def end_active_task(self):
        """
        结束业务任务
        """
        self.active_task = None
    
    def interrupted_active_task(self):
        """
        中断活跃任务
        """

        self.paused_tasks.append(self.active_task) 
        self.active_task = None
    
    def resumed_active_task(self, flow_id:str | None = None) -> bool:
       
        """
        恢复业务任务
        Args:
            flow_id (str | None): 流程ID

        Returns:
            bool: 返回Ture表示恢复成功， False表示恢复失败
        
        """

        # 1. 栈中是否存在中断的业务任务
        if not self.paused_tasks:
            return False
        
        # 2. 判断业务流程id是否存在

        # 如果没传flow_id
        if flow_id is None:
            # 恢复栈顶的
            task = self.paused_tasks.pop()
            self.active_task = task
            return True
        
        # flow_id存在
        for i, pause_task in enumerate(self.paused_tasks):
            # 并且找到了
            if pause_task.flow_id == flow_id:
                # 设置当前激活任务
                self.active_task = pause_task
                # 从paused_tasks列表中删除
                del self.paused_tasks[i]
                return True
        
        return False
            






        # # 恢复最近的任务
        # if not flow_id:
        #     task = self.paused_tasks.pop()
        #     self.active_task = task
        #     return 
        
        # # 精确恢复指定任务
        # for task in self.paused_tasks:
        #     if task.flow_id == flow_id:
        #         self.active_task = task
        #         self.paused_tasks.remove(task) #
        
        # 兜底:如果传入了flow_id，但是未在当前暂停的业务任务列表self.paused_tasks中找到该flow_id对应的任务 --- 则恢复最近的的任务
        # task = self.paused_tasks.pop()
        # self.active_task = task
        # return True
    
    def cancel_active_task(self):
        """
        取消当前任务
        """
        self.active_task = None
        self.active_system_task = None
    
    # --------------槽位相关--------------------------
    def set_slots(self, slots:Dict[str, Any]):  
        """
        设置槽位

        Args:
            slots (Dict[str, Any]): _description_
        """
        self.active_task.slots.update(slots)
    
    def remove_slots(self, slot_name:str):
        """
        移除槽位

        Args:
            slot_name (str): 移除的槽位名
        """
        self.active_task.slots.pop(slot_name)
    
    # --------------当前信息（当前任务、当前session）--------------------------
    def current_active_task(self):
        """
        当前正在执行的任务(系统流程、业务任务)
        先获取系统流程 如果获取不到 则获取业务任务(引擎跑的时候)
        """

        return self.active_system_task or self.active_task

    def current_session(self):
        """
        返回当前session
        """

        # 根据当前会话会话ID找session对象
        for session in self.sessions:
            if session.session_id == self.current_session_id:
                return session
        
        return None

    # --------------session相关的--------------------------
    def start_session(self):
        """
        开启session
        """

        now:float = time.time()
        session = Session(session_id=str(uuid.uuid4()), started_at=now, last_activity_at=now)
        self.sessions.append(session)
        self.current_session_id = session.session_id
    
    def close_session(self):
        """
        关闭当前session
        """
        
        # 修改session的closed_at时间
        self.current_session().closed_at = time.time()
        # 清空当前的session_id
        self.current_session_id = None
    
    def reset_running_state_for_new_session(self):
        """
        如果会话超时(比如超时60min) 则重置当前的状态
        """
        self.active_task = None
        self.active_system_task = None
        self.paused_tasks = []
        self.focused_object = None
        self.pending_turn = None
        # self.current_session_id = None

    # --------------turn相关的--------------------------
    def begin_turn(self, message:UserMessage):
        if self.current_session():
            turn = Turn(turn_id=str(uuid.uuid4()), user_message=message, bot_messages=[])
            self.pending_turn = turn
    
    def commit_turn(self):
        if self.current_session():
            self.current_session().turns.append(self.pending_turn)
            self.pending_turn = None
    
    # --------------FocusedObject相关的--------------------------
    def set_focused_object(self, focused_object:FocusedObject):
        self.focused_object = focused_object





        
        








