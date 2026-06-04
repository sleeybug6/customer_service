from dataclasses import asdict
from typing import Dict, List, Any
from pathlib import Path
import yaml
from atguigu.task.flow.flows import Flow, FlowSlot, FlowsList
from atguigu.task.flow.steps import CollectedFlowStep, FlowStep

YAML_FILE_PATH = Path(__file__).resolve().parents[3] / 'flow_config' / 'user_flows.yml'

'''
yaml -> dict -> 数据模型类
'''


class FlowLoader:
    """
    流程加载器(加载两个yaml文件)
    """

    def load_many(self, paths:List[Path]) -> FlowsList:
        flows: List[Flow] = []
        slots: Dict[str, FlowSlot] = {}

        for path in paths:
            # 加载单个yaml文件
            single_flow_list = self.load(path)

            
            # 获取单个yaml的flows 将其添加到flows中
            flows.extend(single_flow_list.flows)
            # 获取单个yaml的slots 将其添加到slots  --- 后续可考虑去重
            slots.update(single_flow_list.slots)
        


        return FlowsList(flows=flows, slots=slots)

    def load(self, path:Path) -> FlowsList:
        """
        加载单个yaml文件，返回FlowsList

        Args:
            path (Path): yaml文件路径

        Returns:
            FlowsList: _description_
        """
        
        # 打开文件
        with open(path, 'r', encoding='utf-8') as f:
            data:Dict[str, Any] = yaml.safe_load(f)
        
        # 加载slots部分
        slots: Dict[str, FlowSlot] = self._load_slots(data.get('slots',{}))

        # 加载flows部分
        flows: List[Flow] = self._load_flows(data.get('flows', {}), slots)
        

        return FlowsList(flows=flows, slots=slots)


    def _load_slots(self, slots_data:Dict[str, Dict]) -> Dict[str, FlowSlot]:
        """
        加载yaml文件中的slots部分

        Args:
            slots_data (Dict[str, Dict]): 加载yaml文件后转换得到的slots部分的字典类型数据

        Returns:
            Dict[str, FlowSlot]: 返回的结果，例如:
        {
         "order_number":FlowSlot(),
         "order_status":FlowSlot(),
         ...
         }
        """

        slots = {}
        for slot_name, slot_dict in slots_data.items():
            slots[slot_name] = FlowSlot(name=slot_name, **slot_dict)
        return slots

    def _load_flows(self, flows_data: Dict[str, Dict], slots: Dict[str, FlowSlot]) -> List[Flow]:
        """
        加载加载yaml文件中的flows部分

        Args:
            flows_data (Dict[str, Dict]): _description_
            slots (Dict[str, FlowSlot]): _description_

        Returns:
            List[Flow]: _description_
        """
        

        flows: List[Flow] = []
        for flow_id, flow_dict in flows_data.items():
            steps = [FlowStep.from_dict(step) for step in flow_dict.get('steps',[])]
            flows.append(
                Flow(
                    id=flow_id,
                    description=flow_dict.get('description', ''),
                    steps=steps,
                    slots=self._collect_flow_slots(slots, steps),
                    name=flow_dict.get('name')

                )
            )
        
        return flows
    
    def _collect_flow_slots(self, slots: Dict[str, FlowSlot], steps: List[FlowStep]) -> List[FlowSlot]:
        """


        Args:
            slots (Dict[str, FlowSlot]): 业务所有流程用到的所有槽位定义
            steps (List[FlowStep]): 当前流程的所有步骤
        
        Returns:
            List[FlowSlot]: 当前流程要用到的槽位定义
        """

        seen = set()
        flow_slots = []
        for step in steps:
            if not isinstance(step, CollectedFlowStep): #只有collect类型的step才有槽位
                continue

            # 流程中不同的step可能使用到相同的槽位，需要去重
            step_slot_name = step.slot_name
            if step_slot_name in seen:
                continue # 流程中有重复的槽位名字不添加
            
            seen.add(step_slot_name)
            slot = slots.get(step_slot_name)

            # 如果流程当前槽位名字对应的槽位有定义
            if slot is not None:
                flow_slots.append(slot)
        
        return flow_slots





if __name__ == "__main__":
    
    yaml_dir = Path(__file__).resolve().parents[3] / 'flow_config'
    user_flow_path = yaml_dir / 'user_flows.yml'
    system_flow_path = yaml_dir / 'system_flows.yml'
    paths = [user_flow_path, system_flow_path]
    loader = FlowLoader()
    # data = loader.load(user_flow_path)
    flow_list: FlowsList = loader.load_many(paths)

    # 将对象转成字典后写入yaml文件中
    with open('test.yaml', 'w', encoding='utf-8') as f:
        yaml.safe_dump(asdict(flow_list), f, allow_unicode=True)


    # with open('test.yaml', 'w', encoding='utf-8') as f:
    #     yaml.safe_dump(data, f)







    
