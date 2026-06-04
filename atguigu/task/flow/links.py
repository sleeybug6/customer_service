from dataclasses import dataclass

@dataclass(slots=True)
class FlowStepLink:
    """
    模板边(基类)
    """
    target:str # 下一个步骤(节点)的ID

@dataclass(slots=True)
class FlowStepStaticLink(FlowStepLink):
    """
    固定的下一个边(无条件)，如next:ask_order_number
    """
    pass

@dataclass(slots=True)
class FlowStepConditionalLink(FlowStepLink):
    """
    带条件的边, 如
    next:
        - if: "slots.get('product_id')"
          then: respond
    """
    condition:str

class FlowStepFallbackLink(FlowStepLink):
    """
    条件边中的else分支，如
    next:
        - else: missing_product_context
    """
    pass
