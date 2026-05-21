from pydantic import BaseModel
from typing import Optional


class GroupResponse(BaseModel):
    """分组响应模型"""
    MDC: Optional[str] = None
    ADRG: Optional[str] = None
    ADRG_NAME: Optional[str] = None
    DRG: Optional[str] = None
    DRG_NAME: Optional[str] = None
    COMPLICATION: Optional[str] = None
    STATUS: str

    class Config:
        json_schema_extra = {
            "example": {
                "MDC": "MDCZ",
                "ADRG": "ZZ1",
                "ADRG_NAME": "多发性重要创伤无手术",
                "DRG": "ZZ19",
                "DRG_NAME": "多发性重要创伤无手术",
                "COMPLICATION": "NONE",
                "STATUS": "SUCCESS"
            }
        }
