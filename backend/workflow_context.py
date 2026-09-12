from typing import Optional
from pydantic import BaseModel
from Classification import ProductContext


class WorkflowContext(BaseModel):
    product: ProductContext

    jurisdiction: Optional[dict] = None

    ip_assessment: Optional[dict] = None
    regulatory_assessment: Optional[dict] = None
    tkdl_assessment: Optional[dict] = None
    abs_assessment: Optional[dict] = None

    roadmap: Optional[dict] = None